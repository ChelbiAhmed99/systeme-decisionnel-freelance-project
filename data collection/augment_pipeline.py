"""
Pipeline d'augmentation de données — Agence de Voyage
=======================================================
Prend les tables réelles (mais petites) fournies par l'utilisateur
(customers, hotels, flights, packages, bookings, cities, countries,
continents, flight_price_list) et les enrichit par data augmentation
(bootstrap + jitter contrôlé + génération conditionnée par segment)
pour produire un jeu de données à l'échelle attendue par le pipeline
ML/BI du notebook, tout en restant ancré dans les données réelles
(mêmes villes, mêmes hôtels, mêmes clients de base, mêmes tarifs).
"""
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

RAW_DIR = "/home/claude/work/data"
OUT_DIR = "/home/claude/work/data_augmented"
os.makedirs(OUT_DIR, exist_ok=True)

# Facteur de conversion indicatif EUR -> TND (les tables sources sont en EUR)
EUR_TO_TND = 3.3

# ---------------------------------------------------------------------------
# 0. Chargement des tables réelles (seed)
# ---------------------------------------------------------------------------
customers = pd.read_csv(f"{RAW_DIR}/customers.csv")
hotels_raw = pd.read_csv(f"{RAW_DIR}/hotels.csv")
flights_raw = pd.read_csv(f"{RAW_DIR}/flights.csv")
price_list = pd.read_csv(f"{RAW_DIR}/flight_price_list.csv")
packages = pd.read_csv(f"{RAW_DIR}/packages.csv")
bookings = pd.read_csv(f"{RAW_DIR}/bookings.csv")
cities = pd.read_csv(f"{RAW_DIR}/cities.csv")
countries = pd.read_csv(f"{RAW_DIR}/countries.csv")
continents = pd.read_csv(f"{RAW_DIR}/continents.csv")

# ---------------------------------------------------------------------------
# Constantes réutilisées (mêmes que la génération synthétique d'origine)
# ---------------------------------------------------------------------------
VILLES_TN = ["Tunis", "Sfax", "Sousse", "Bizerte", "Gabès", "Kairouan", "Nabeul", "Monastir", "Gafsa", "Ariana"]
SEGMENTS_LATENTS = ["Aventurier", "Farniente", "Culturel", "Luxe", "Familial", "Budget"]
TYPES_VOYAGE = ["Plage", "Montagne", "Culturel", "Aventure", "Urbain", "Croisière", "Rural/Nature"]
ACTIVITES_POSSIBLES = ["Randonnée", "Plongée", "Musées", "Shopping", "Gastronomie", "Vie nocturne",
                       "Sports nautiques", "Ski", "Safari", "Spa & bien-être", "Photographie", "Plage détente"]
SAISONS = ["Printemps", "Été", "Automne", "Hiver"]
CANAUX = ["Agence physique", "Site web", "Application mobile", "Call center"]

SEGMENT_TYPE_AFFINITY = {
    "Aventurier": {"Aventure": 0.40, "Montagne": 0.25, "Rural/Nature": 0.15, "Culturel": 0.10, "Plage": 0.05, "Urbain": 0.03, "Croisière": 0.02},
    "Farniente":  {"Plage": 0.50, "Croisière": 0.20, "Rural/Nature": 0.10, "Urbain": 0.08, "Culturel": 0.07, "Montagne": 0.03, "Aventure": 0.02},
    "Culturel":   {"Culturel": 0.45, "Urbain": 0.25, "Rural/Nature": 0.10, "Plage": 0.08, "Montagne": 0.07, "Aventure": 0.03, "Croisière": 0.02},
    "Luxe":       {"Croisière": 0.30, "Plage": 0.25, "Urbain": 0.20, "Culturel": 0.15, "Montagne": 0.05, "Aventure": 0.03, "Rural/Nature": 0.02},
    "Familial":   {"Plage": 0.35, "Urbain": 0.20, "Culturel": 0.15, "Rural/Nature": 0.15, "Montagne": 0.08, "Aventure": 0.04, "Croisière": 0.03},
    "Budget":     {"Rural/Nature": 0.25, "Plage": 0.20, "Culturel": 0.20, "Urbain": 0.15, "Montagne": 0.12, "Aventure": 0.05, "Croisière": 0.03},
}
SEGMENT_BUDGET_RANGE = {
    "Aventurier": (2000, 6000), "Farniente": (2500, 7000), "Culturel": (1800, 5500),
    "Luxe": (7000, 20000), "Familial": (3000, 9000), "Budget": (800, 2500),
}

# Assignation éditoriale du type de voyage dominant par ville réelle (connaissance tourisme générale)
CITY_TYPE_VOYAGE = {
    "ROME": "Culturel", "VENICE": "Culturel", "MILANO": "Urbain", "BARCELONA": "Plage",
    "ATHENS": "Culturel", "PORTO": "Culturel", "ANTALYA": "Plage", "ISTANBUL": "Culturel",
    "BERLIN": "Urbain", "BUCHAREST": "Urbain", "MOSCOW": "Urbain", "AMSTERDAM": "Urbain",
    "PARIS": "Urbain", "MARSEILLE": "Plage", "NISA": "Plage", "SANKT PETERSBURG": "Culturel",
    "SYDNEY": "Plage",
}
CONT_FR = {
    "EUROPE": "Europe", "AFRICA": "Afrique", "ASIA": "Asie",
    "AUSTRALIA": "Océanie", "NORTH AMERICA": "Amérique du Nord",
    "SOUTH AMERICA": "Amérique du Sud", "ANTARCTICA": "Antarctique",
}

# Ville "hub" de l'agence : celle présente sur (quasi) toutes les liaisons du seed = 16 (Bucarest)
HUB_CITY_ID = 16

rng = np.random.RandomState(RANDOM_SEED)

# ===========================================================================
# 1. DESTINATIONS — ancrées sur les villes réelles (cities/countries/continents)
# ===========================================================================
def build_destinations():
    geo = cities.merge(countries, left_on="id_country", right_on="ctryID") \
                .merge(continents, left_on="id_cont", right_on="contID")

    # popularité réelle = nb de réservations historiques (bookings -> packages -> ville)
    real_pop = bookings.merge(packages, left_on="bookPackageID", right_on="packID") \
                        .groupby("packLocationID").size()

    rows = []
    for _, c in geo.iterrows():
        type_voyage = CITY_TYPE_VOYAGE.get(c["citName"], rng.choice(TYPES_VOYAGE))
        base_pop = real_pop.get(c["citID"], 0)
        popularite = np.clip(15 + base_pop * 12 + rng.uniform(-5, 5), 1, 100)
        n_act = rng.randint(2, 5)
        activites = list(rng.choice(ACTIVITES_POSSIBLES, size=n_act, replace=False))
        saison = rng.choice(["Hiver", "Été"], p=[0.6, 0.4]) if type_voyage == "Montagne" \
                 else rng.choice(SAISONS, p=[0.20, 0.40, 0.20, 0.20])
        note = float(np.clip(rng.normal(4.1, 0.35), 2.5, 5.0))
        rows.append({
            "destination_id": f"DST{int(c['citID']):04d}",
            "nom_destination": c["citName"].title(),
            "pays_continent": CONT_FR.get(c["contName"], c["contName"].title()),
            "type_voyage": type_voyage,
            "popularite_score": round(popularite, 1),
            "activites_disponibles": ";".join(activites),
            "saison_ideale": saison,
            "note_moyenne_destination": round(note, 2),
            "_citID": int(c["citID"]),
        })
    return pd.DataFrame(rows)

destinations_df = build_destinations()

# ---- budget_moyen_tnd : dérivé des vrais tarifs hôtels/vols par destination, EUR->TND ----
hot_avg = hotels_raw.groupby("hotLocID")["hotPricePerNight"].mean() * 7  # ~ budget hébergement/semaine
fli_avg = pd.concat([
    flights_raw.groupby("fliStartPoint")["fliPrice"].mean(),
    flights_raw.groupby("fliEndPoint")["fliPrice"].mean(),
]).groupby(level=0).mean()

def estimate_budget(citid):
    h = hot_avg.get(citid, np.nan)
    f = fli_avg.get(citid, np.nan)
    if np.isnan(h) and np.isnan(f):
        return None
    h = h if not np.isnan(h) else fli_avg.mean() * 2
    f = f if not np.isnan(f) else fli_avg.mean()
    return (h + f) * EUR_TO_TND

est = destinations_df["_citID"].map(estimate_budget)
fallback_by_type = destinations_df.assign(_e=est).groupby("type_voyage")["_e"].transform("mean")
destinations_df["budget_moyen_tnd"] = est.fillna(fallback_by_type).fillna(2500).round(0)
destinations_df = destinations_df.drop(columns="_citID")

# ===========================================================================
# 2. HÔTELS — à partir de hotels.csv, augmentés pour couvrir toutes les destinations
# ===========================================================================
def build_hotels(dest_df, target_per_dest=3):
    real = hotels_raw.copy()
    real["destination_id"] = real["hotLocID"].apply(lambda x: f"DST{int(x):04d}")
    dest_by_type = dest_df.set_index("destination_id")["type_voyage"]

    rows = []
    hid = 1
    for _, d in dest_df.iterrows():
        pool = real[real["destination_id"] == d["destination_id"]]
        if len(pool) == 0:
            # pas d'hôtel réel pour cette ville -> on clone un hôtel réel d'une ville
            # au profil de voyage similaire (même type_voyage) et on ajuste son prix
            similar = dest_df[(dest_df["type_voyage"] == d["type_voyage"]) & (dest_df["destination_id"] != d["destination_id"])]
            donor_ids = similar["destination_id"].tolist()
            donor_pool = real[real["destination_id"].isin(donor_ids)]
            template = donor_pool.sample(1, random_state=rng.randint(1e6)).iloc[0] if len(donor_pool) else real.sample(1).iloc[0]
        else:
            template = pool.sample(1, random_state=rng.randint(1e6)).iloc[0]

        n_needed = max(target_per_dest, len(pool) + 1)
        for k in range(n_needed):
            src = pool.sample(1).iloc[0] if (k < len(pool)) else template
            jitter = rng.uniform(0.85, 1.20)
            etoiles = int(np.clip(rng.choice([2, 3, 4, 5], p=[0.15, 0.35, 0.35, 0.15]), 2, 5))
            prix = round(float(src["hotPricePerNight"]) * jitter * EUR_TO_TND, 0)
            rows.append({
                "hotel_id": f"HTL{hid:05d}",
                "destination_id": d["destination_id"],
                "nom_hotel": f"{src['hotName'].title()} {'' if k == 0 else k+1}".strip() if k < len(pool) else f"Hôtel {d['nom_destination']} {k+1}",
                "categorie_etoiles": etoiles,
                "prix_nuit_tnd": prix,
                "capacite_chambres": int(rng.randint(30, 400)),
            })
            hid += 1
    return pd.DataFrame(rows)

hotels_df = build_hotels(destinations_df, target_per_dest=3)

# ===========================================================================
# 3. VOLS — à partir de flights.csv + flight_price_list.csv, augmentés
# ===========================================================================
def build_flights(dest_df, target_per_dest=2):
    real = flights_raw.copy()
    compagnies = ["Tunisair", "Nouvelair", "Air France", "Turkish Airlines", "Emirates", "Ryanair", "Lufthansa"]
    classes = ["Economy", "Economy", "Economy", "Business", "First"]

    real_by_dest = {}
    for _, r in real.iterrows():
        other = r["fliEndPoint"] if r["fliStartPoint"] == HUB_CITY_ID else r["fliStartPoint"]
        real_by_dest.setdefault(other, []).append(r)

    rows = []
    fid = 1
    global_avg_price = real["fliPrice"].mean()
    for _, d in dest_df.iterrows():
        citid = int(d["destination_id"].replace("DST", ""))
        pool = real_by_dest.get(citid, [])
        base_price = np.mean([p["fliPrice"] for p in pool]) if pool else \
            d["budget_moyen_tnd"] / EUR_TO_TND * rng.uniform(0.18, 0.30)

        n_needed = max(target_per_dest, len(pool))
        for k in range(n_needed):
            jitter = rng.uniform(0.85, 1.25)
            prix_eur = base_price * jitter
            rows.append({
                "flight_id": f"FLT{fid:05d}",
                "destination_id": d["destination_id"],
                "compagnie": rng.choice(compagnies),
                "classe": rng.choice(classes),
                "prix_vol_tnd": round(prix_eur * EUR_TO_TND, 0),
                "duree_heures": round(float(np.clip(rng.normal(3.5, 2.0), 1.0, 14.0)), 1),
            })
            fid += 1
    return pd.DataFrame(rows)

flights_df = build_flights(destinations_df, target_per_dest=2)

# ===========================================================================
# 4. CLIENTS — bootstrap des 11 clients réels -> N_CLIENTS, + attributs dérivés
# ===========================================================================
def build_clients(real_customers, n):
    first_names = real_customers["custName"].tolist()
    last_names = real_customers["custSurname"].tolist()
    rows = []
    for i in range(1, n + 1):
        if i <= len(real_customers):
            src = real_customers.iloc[i - 1]
            prenom, nom = src["custName"], src["custSurname"]
        else:
            prenom = rng.choice(first_names)
            nom = rng.choice(last_names)

        segment = rng.choice(SEGMENTS_LATENTS, p=[0.18, 0.18, 0.16, 0.12, 0.20, 0.16])
        age = int(np.clip(rng.normal(38, 12), 18, 75))
        revenu = int(np.clip(rng.normal(3200, 1400), 700, 15000))
        anciennete_jours = rng.randint(30, 2200)
        date_inscription = datetime(2026, 9, 15) - timedelta(days=int(anciennete_jours))
        rows.append({
            "client_id": f"CLI{i:05d}",
            "prenom": prenom,
            "nom": nom,
            "age": age,
            "sexe": rng.choice(["F", "M"]),
            "ville": rng.choice(VILLES_TN),
            "statut_familial": rng.choice(["Célibataire", "Marié(e)", "Marié(e) avec enfants"], p=[0.4, 0.25, 0.35]),
            "revenu_mensuel_tnd": revenu,
            "segment_latent": segment,
            "date_inscription": date_inscription.date().isoformat(),
            "source_client": "réel" if i <= len(real_customers) else "augmenté",
        })
    return pd.DataFrame(rows)

N_CLIENTS = 500
clients_df = build_clients(customers, N_CLIENTS)

# ===========================================================================
# 5. PRÉFÉRENCES — dérivées du segment (comme l'original) pour tous les clients
# ===========================================================================
def build_preferences(clients_df):
    rows = []
    for _, c in clients_df.iterrows():
        seg = c["segment_latent"]
        affin = SEGMENT_TYPE_AFFINITY[seg]
        type_pref = rng.choice(list(affin.keys()), p=list(affin.values()))
        budget_min, budget_max = SEGMENT_BUDGET_RANGE[seg]
        n_act = rng.randint(2, 4)
        activites_pref = list(rng.choice(ACTIVITES_POSSIBLES, size=n_act, replace=False))
        rows.append({
            "client_id": c["client_id"],
            "type_voyage_prefere": type_pref,
            "budget_max_tnd": round(rng.uniform(budget_min, budget_max), 0),
            "activites_preferees": ";".join(activites_pref),
            "saison_preferee": rng.choice(SAISONS),
            "voyage_frequent": rng.choice(["Oui", "Non"], p=[0.35, 0.65]),
        })
    return pd.DataFrame(rows)

preferences_df = build_preferences(clients_df)

# ===========================================================================
# 6. RÉSERVATIONS — bootstrap des 16 réservations réelles (bookings.csv) -> N_RESERVATIONS
#    puis génération conditionnée profil client (comme la génération d'origine)
# ===========================================================================
def choose_destination_for_client(client_row, pref_row, dest_df):
    seg = client_row["segment_latent"]
    affin = SEGMENT_TYPE_AFFINITY[seg]
    weights = dest_df["type_voyage"].map(affin).fillna(0.01).values.astype(float)
    budget_gap = np.abs(dest_df["budget_moyen_tnd"].values - pref_row["budget_max_tnd"])
    budget_weight = 1 / (1 + budget_gap / 1500.0)
    pop_weight = dest_df["popularite_score"].values / 100.0
    final_w = (weights * 0.55 + budget_weight * 0.30 + pop_weight * 0.15) + 1e-6
    final_w = final_w / final_w.sum()
    idx = rng.choice(dest_df.index, p=final_w)
    return dest_df.loc[idx]

def build_reservations(n, clients_df, pref_df, dest_df, hotels_df, flights_df):
    rows = []
    clients_indexed = clients_df.set_index("client_id")
    prefs_indexed = pref_df.set_index("client_id")
    client_ids = clients_df["client_id"].values

    for i in range(1, n + 1):
        cid = rng.choice(client_ids)
        crow, prow = clients_indexed.loc[cid], prefs_indexed.loc[cid]
        drow = choose_destination_for_client(crow, prow, dest_df)
        h_candidates = hotels_df[hotels_df["destination_id"] == drow["destination_id"]]
        f_candidates = flights_df[flights_df["destination_id"] == drow["destination_id"]]
        hrow = h_candidates.sample(1, random_state=rng.randint(1e6)).iloc[0]
        frow = f_candidates.sample(1, random_state=rng.randint(1e6)).iloc[0]

        nb_personnes = rng.choice([1, 2, 3, 4, 5], p=[0.25, 0.35, 0.15, 0.15, 0.10])
        nb_nuits = rng.randint(2, 12)
        montant = hrow["prix_nuit_tnd"] * nb_nuits + frow["prix_vol_tnd"] * nb_personnes
        montant *= rng.uniform(0.95, 1.10)

        annee = rng.choice([2024, 2025, 2026], p=[0.30, 0.42, 0.28])
        mois = rng.randint(1, 13)
        jour = rng.randint(1, 28)
        date_depart = datetime(int(annee), int(mois), int(jour))
        date_reservation = date_depart - timedelta(days=int(rng.uniform(5, 120)))
        date_retour = date_depart + timedelta(days=int(nb_nuits))

        statut = rng.choice(["Confirmée", "Annulée"], p=[0.87, 0.13])
        satisfaction = np.nan if statut == "Annulée" else float(np.clip(
            rng.normal(drow["note_moyenne_destination"], 0.5), 1, 5))

        rows.append({
            "reservation_id": f"RES{i:06d}",
            "client_id": cid,
            "destination_id": drow["destination_id"],
            "hotel_id": hrow["hotel_id"],
            "flight_id": frow["flight_id"],
            "date_reservation": date_reservation.date().isoformat(),
            "date_depart": date_depart.date().isoformat(),
            "date_retour": date_retour.date().isoformat(),
            "nb_personnes": nb_personnes,
            "nb_nuits": nb_nuits,
            "montant_total_tnd": round(montant, 2),
            "canal_vente": rng.choice(CANAUX, p=[0.20, 0.45, 0.25, 0.10]),
            "statut_reservation": statut,
            "note_satisfaction": satisfaction,
            "source": "généré",
        })

    # --- on ancre 16 réservations réelles (bookings.csv) au tout début, mappées aux ids augmentés ---
    real_join = bookings.merge(packages, left_on="bookPackageID", right_on="packID")
    real_rows = []
    for j, (_, b) in enumerate(real_join.iterrows(), start=1):
        cid = f"CLI{int(b['bookCustomerID']):05d}"
        did = f"DST{int(b['packLocationID']):04d}"
        if did not in dest_df["destination_id"].values or cid not in clients_df["client_id"].values:
            continue
        h_candidates = hotels_df[hotels_df["destination_id"] == did]
        f_candidates = flights_df[flights_df["destination_id"] == did]
        hrow = h_candidates.sample(1, random_state=j).iloc[0]
        frow = f_candidates.sample(1, random_state=j).iloc[0]
        date_depart = pd.to_datetime(b.get("packStartDate", "2017-09-20"), errors="coerce")
        date_depart = date_depart if pd.notna(date_depart) else datetime(2024, 6, 1)
        date_retour = pd.to_datetime(b.get("packEndDate", None), errors="coerce")
        nb_nuits = max(1, (date_retour - date_depart).days) if pd.notna(date_retour) else 5
        real_rows.append({
            "reservation_id": f"RESR{j:04d}",
            "client_id": cid,
            "destination_id": did,
            "hotel_id": hrow["hotel_id"],
            "flight_id": frow["flight_id"],
            "date_reservation": (date_depart - timedelta(days=30)).date().isoformat(),
            "date_depart": date_depart.date().isoformat(),
            "date_retour": (date_depart + timedelta(days=int(nb_nuits))).date().isoformat(),
            "nb_personnes": int(b.get("packPplNo", 2)),
            "nb_nuits": int(nb_nuits),
            "montant_total_tnd": round(float(b["packPrice"]) * int(b.get("bookNoOfPackPurchased", 1)) * EUR_TO_TND, 2),
            "canal_vente": rng.choice(CANAUX, p=[0.20, 0.45, 0.25, 0.10]),
            "statut_reservation": "Confirmée",
            "note_satisfaction": float(np.clip(rng.normal(4.2, 0.4), 1, 5)),
            "source": "réel",
        })
    return pd.DataFrame(real_rows + rows)

N_RESERVATIONS = 4000
reservations_df = build_reservations(N_RESERVATIONS, clients_df, preferences_df, destinations_df, hotels_df, flights_df)

# --- injection volontaire de bruit (valeurs manquantes, doublons, anomalies) : identique à l'original ---
res_dirty = reservations_df.copy()
for col, frac in [("nb_personnes", 0.02), ("canal_vente", 0.03), ("montant_total_tnd", 0.015)]:
    idx = res_dirty.sample(frac=frac, random_state=1).index
    res_dirty.loc[idx, col] = np.nan
dupes = res_dirty.sample(30, random_state=2)
res_dirty = pd.concat([res_dirty, dupes], ignore_index=True)
anom_idx = res_dirty.sample(15, random_state=3).index
res_dirty.loc[anom_idx, "montant_total_tnd"] = res_dirty.loc[anom_idx, "montant_total_tnd"] * rng.uniform(8, 15)
anom_idx2 = res_dirty.sample(10, random_state=4).index
res_dirty.loc[anom_idx2, "nb_personnes"] = rng.choice([0, -1, 50], size=len(anom_idx2))
reservations_df = res_dirty

# ===========================================================================
# Sauvegarde
# ===========================================================================
clients_df.to_csv(f"{OUT_DIR}/clients.csv", index=False)
destinations_df.to_csv(f"{OUT_DIR}/destinations.csv", index=False)
hotels_df.to_csv(f"{OUT_DIR}/hotels.csv", index=False)
flights_df.to_csv(f"{OUT_DIR}/flights.csv", index=False)
preferences_df.to_csv(f"{OUT_DIR}/preferences.csv", index=False)
reservations_df.to_csv(f"{OUT_DIR}/reservations.csv", index=False)

print("clients:", clients_df.shape)
print("destinations:", destinations_df.shape)
print("hotels:", hotels_df.shape)
print("flights:", flights_df.shape)
print("preferences:", preferences_df.shape)
print("reservations:", reservations_df.shape)
print("clients réels vs augmentés:\n", clients_df["source_client"].value_counts())
print("reservations réelles vs générées:\n", reservations_df["source"].value_counts())
print(reservations_df.isna().sum())
