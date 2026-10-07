# -*- coding: utf-8 -*-
"""
Enrichissement du catalogue de destinations + hôtels/vols associés + génération
de réservations réalistes, pour combler les 4 types de voyage absents du
catalogue actuel (Montagne, Aventure, Croisière, Rural/Nature) et diversifier
les continents (ajout Afrique / Amérique).
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RANDOM_SEED = 42
rng = np.random.RandomState(RANDOM_SEED)

clients_df = pd.read_csv("clients.csv")
destinations_df = pd.read_csv("destinations.csv")
hotels_df = pd.read_csv("hotels.csv")
flights_df = pd.read_csv("flights.csv")
preferences_df = pd.read_csv("preferences.csv")
reservations_df = pd.read_csv("reservations.csv")

ACTIVITES_POSSIBLES = ["Randonnée", "Plongée", "Musées", "Shopping", "Gastronomie", "Vie nocturne",
                        "Sports nautiques", "Ski", "Safari", "Spa & bien-être", "Photographie", "Plage détente"]

# ---------------------------------------------------------------------------
# 1) NOUVELLES DESTINATIONS — comble les 4 types manquants + diversifie
#    les continents (Afrique, Amérique quasi absents du catalogue actuel).
# ---------------------------------------------------------------------------
new_destinations = [
    # (nom, continent, type_voyage, popularite, activites(list), saison, note, budget_moyen)
    ("Chamonix",        "Europe",   "Montagne",     28.5, ["Randonnée", "Ski", "Photographie"], "Hiver",     4.55, 2650),
    ("Innsbruck",       "Europe",   "Montagne",     24.1, ["Ski", "Randonnée", "Gastronomie"],  "Hiver",     4.30, 2180),
    ("Interlaken",      "Europe",   "Montagne",     26.7, ["Randonnée", "Photographie", "Ski"], "Été",       4.62, 2890),
    ("Banff",           "Amérique", "Montagne",     22.3, ["Randonnée", "Ski", "Photographie"], "Hiver",     4.48, 3450),
    ("Queenstown",      "Océanie",  "Montagne",     19.8, ["Randonnée", "Ski", "Sports nautiques"], "Hiver", 4.41, 3120),

    ("Marrakech",       "Afrique",  "Aventure",     33.4, ["Randonnée", "Safari", "Shopping"],  "Printemps", 4.38, 1450),
    ("Serengeti",       "Afrique",  "Aventure",     21.6, ["Safari", "Photographie", "Randonnée"], "Été",    4.71, 4200),
    ("Ushuaia",         "Amérique", "Aventure",     15.2, ["Randonnée", "Photographie", "Sports nautiques"], "Été", 4.33, 3980),
    ("Sapa",             "Asie",    "Aventure",     18.7, ["Randonnée", "Photographie", "Gastronomie"], "Automne", 4.44, 1180),
    ("Moshi",            "Afrique", "Aventure",     16.9, ["Randonnée", "Safari"],              "Automne",  4.52, 2760),

    ("Miami",            "Amérique","Croisière",    30.2, ["Plage détente", "Sports nautiques", "Vie nocturne"], "Hiver", 4.19, 3340),
    ("Santorini",         "Europe", "Croisière",    38.9, ["Plage détente", "Gastronomie", "Photographie"], "Été", 4.68, 2790),
    ("Dubrovnik",         "Europe", "Croisière",    24.4, ["Plage détente", "Vie nocturne", "Photographie"], "Été", 4.36, 2410),
    ("Fidji",             "Océanie","Croisière",    20.1, ["Plage détente", "Sports nautiques", "Spa & bien-être"], "Été", 4.60, 3990),
    ("Singapour",          "Asie",  "Croisière",    27.8, ["Shopping", "Gastronomie", "Vie nocturne"], "Été", 4.41, 3210),

    ("Ubud",              "Asie",   "Rural/Nature", 29.6, ["Randonnée", "Spa & bien-être", "Photographie"], "Automne", 4.57, 1620),
    ("Toscane",           "Europe", "Rural/Nature", 26.3, ["Gastronomie", "Randonnée", "Photographie"], "Automne", 4.66, 2340),
    ("Provence",          "Europe", "Rural/Nature", 23.9, ["Gastronomie", "Shopping", "Photographie"], "Printemps", 4.44, 2190),
    ("Kerala",             "Asie",  "Rural/Nature", 17.5, ["Randonnée", "Spa & bien-être", "Gastronomie"], "Hiver", 4.39, 1340),
    ("Monteverde",        "Amérique","Rural/Nature",14.8, ["Randonnée", "Safari", "Photographie"], "Printemps", 4.35, 2680),

    ("Cancun",             "Amérique","Plage",      31.7, ["Plage détente", "Sports nautiques", "Vie nocturne"], "Hiver", 4.27, 2980),
    ("Zanzibar",           "Afrique", "Plage",      22.8, ["Plage détente", "Plongée", "Sports nautiques"], "Été", 4.53, 1980),
    ("Nha Trang",            "Asie",  "Plage",      16.4, ["Plage détente", "Sports nautiques", "Shopping"], "Été", 4.12, 1240),
    ("Malaga",              "Europe","Plage",       21.2, ["Plage détente", "Gastronomie", "Vie nocturne"], "Été", 4.20, 1740),

    ("Le Caire",             "Afrique","Culturel",  25.9, ["Musées", "Photographie", "Shopping"], "Hiver",   4.31, 1420),
    ("Kyoto",                "Asie",   "Culturel",  30.4, ["Musées", "Photographie", "Gastronomie"], "Printemps", 4.74, 2870),

    ("New York",            "Amérique","Urbain",    36.8, ["Shopping", "Musées", "Vie nocturne"], "Automne", 4.29, 3650),
    ("Dubai",                "Asie",   "Urbain",    34.1, ["Shopping", "Vie nocturne", "Spa & bien-être"], "Hiver", 4.42, 3180),
]

next_dst_num = int(destinations_df["destination_id"].str.replace("DST", "").astype(int).max()) + 1
rows = []
for i, (nom, cont, typ, pop, acts, saison, note, budget) in enumerate(new_destinations):
    did = f"DST{next_dst_num + i:04d}"
    rows.append({
        "destination_id": did, "nom_destination": nom, "pays_continent": cont,
        "type_voyage": typ, "popularite_score": pop, "activites_disponibles": ";".join(acts),
        "saison_ideale": saison, "note_moyenne_destination": note, "budget_moyen_tnd": float(budget),
    })
new_dest_df = pd.DataFrame(rows)
destinations_enriched = pd.concat([destinations_df, new_dest_df], ignore_index=True)

print(f"Destinations : {len(destinations_df)} -> {len(destinations_enriched)}")
print(destinations_enriched["type_voyage"].value_counts())
print(destinations_enriched["pays_continent"].value_counts())

# ---------------------------------------------------------------------------
# 2) HÔTELS & VOLS pour chaque nouvelle destination (3 hôtels, 2 vols — même
#    convention que le catalogue existant), prix cohérents avec budget_moyen_tnd
#    et distance approximative du continent (vols plus chers hors Europe/Afrique).
# ---------------------------------------------------------------------------
COMPAGNIES = ["Turkish Airlines", "Tunisair", "Nouvelair", "Emirates", "Lufthansa", "Air France", "Ryanair"]
CLASSES = ["Economy", "Economy", "Economy", "Business", "First"]  # pondéré vers Economy
CONTINENT_FLIGHT_BASE = {"Europe": 350, "Afrique": 420, "Asie": 650, "Amérique": 1150, "Océanie": 1400}
HOTEL_STAR_WEIGHTS = [0.05, 0.20, 0.40, 0.25, 0.10]  # 1..5 étoiles

next_htl_num = int(hotels_df["hotel_id"].str.replace("HTL", "").astype(int).max()) + 1
next_flt_num = int(flights_df["flight_id"].str.replace("FLT", "").astype(int).max()) + 1

new_hotels, new_flights = [], []
htl_counter, flt_counter = next_htl_num, next_flt_num
for _, d in new_dest_df.iterrows():
    did, budget = d["destination_id"], d["budget_moyen_tnd"]
    avg_nights = 6.5
    base_price_night = max(60, budget / avg_nights)
    for h in range(3):
        stars = int(rng.choice([1, 2, 3, 4, 5], p=HOTEL_STAR_WEIGHTS))
        price = round(base_price_night * rng.uniform(0.75, 1.35) * (1 + 0.12 * (stars - 3)), 0)
        new_hotels.append({
            "hotel_id": f"HTL{htl_counter:05d}", "destination_id": did,
            "nom_hotel": f"Hôtel {d['nom_destination']} {h+1}",
            "categorie_etoiles": stars, "prix_nuit_tnd": float(max(price, 40)),
            "capacite_chambres": int(rng.randint(40, 400)),
        })
        htl_counter += 1
    base_flight = CONTINENT_FLIGHT_BASE[d["pays_continent"]]
    for f in range(2):
        classe = rng.choice(CLASSES)
        mult = {"Economy": 1.0, "Business": 1.9, "First": 2.8}[classe]
        price = round(base_flight * mult * rng.uniform(0.85, 1.2), 0)
        duree = {"Europe": rng.uniform(1.5, 4.5), "Afrique": rng.uniform(2.0, 5.0),
                 "Asie": rng.uniform(4.0, 9.0), "Amérique": rng.uniform(9.0, 13.5),
                 "Océanie": rng.uniform(14.0, 20.0)}[d["pays_continent"]]
        new_flights.append({
            "flight_id": f"FLT{flt_counter:05d}", "destination_id": did,
            "compagnie": rng.choice(COMPAGNIES), "classe": classe,
            "prix_vol_tnd": float(price), "duree_heures": round(float(duree), 1),
        })
        flt_counter += 1

new_hotels_df = pd.DataFrame(new_hotels)
new_flights_df = pd.DataFrame(new_flights)
hotels_enriched = pd.concat([hotels_df, new_hotels_df], ignore_index=True)
flights_enriched = pd.concat([flights_df, new_flights_df], ignore_index=True)
print(f"Hôtels : {len(hotels_df)} -> {len(hotels_enriched)}")
print(f"Vols   : {len(flights_df)} -> {len(flights_enriched)}")

# ---------------------------------------------------------------------------
# 3) RÉSERVATIONS pour les nouvelles destinations — nécessaire pour que
#    destination_features (nb_reservations, revenu_genere, satisfaction) et
#    les features RFM clients ne soient pas nulles/creuses sur le nouveau
#    catalogue. On cible les clients dont le type de voyage préféré
#    correspond (signal fort), avec un peu de bruit pour rester réaliste.
# ---------------------------------------------------------------------------
CANAUX = ["Site web", "Application mobile", "Agence physique", "Call center"]
CANAL_P = [0.42, 0.25, 0.20, 0.13]
CANCEL_RATE = 0.13

client_prefs = clients_df.merge(preferences_df, on="client_id", how="left")
# Les identifiants existants sont hétérogènes (RESRxxxx / RESxxxxxx, anomalies injectées
# volontairement pour le nettoyage) : on prend le prefixe le plus utilisé et on numérote
# les nouvelles lignes dans un espace clairement disjoint pour éviter toute collision.
res_counter = 1
NEW_RES_PREFIX = "RESE"  # E = "Enrichissement" ; jamais utilisé dans le jeu d'origine

new_reservations = []
dest_htl_map = new_hotels_df.groupby("destination_id")["hotel_id"].apply(list).to_dict()
dest_flt_map = new_flights_df.groupby("destination_id")["flight_id"].apply(list).to_dict()

for _, d in new_dest_df.iterrows():
    did, typ, budget, pop, saison_dest, note_dest = (
        d["destination_id"], d["type_voyage"], d["budget_moyen_tnd"], d["popularite_score"],
        d["saison_ideale"], d["note_moyenne_destination"])

    # clients dont le type préféré correspond (public cible principal)
    matching = client_prefs[client_prefs["type_voyage_prefere"] == typ]
    # + un échantillon de clients "exploratoires" hors profil, pour du bruit réaliste
    others = client_prefs[client_prefs["type_voyage_prefere"] != typ].sample(
        n=min(15, len(client_prefs)), random_state=int(pop * 100) % (2**31))

    # Volume calibré pour retrouver une densité d'interaction comparable à celle
    # des destinations existantes (~207 réservations confirmées/destination en moyenne),
    # modulée par la popularité relative de chaque nouvelle destination.
    n_bookings = int(np.clip(pop * 8.5, 130, 300))
    pool = pd.concat([matching, others], ignore_index=True)
    if len(pool) == 0:
        continue
    chosen = pool.sample(n=n_bookings, replace=len(pool) < n_bookings,
                          random_state=int(pop * 37) % (2**31))

    for _, cli in chosen.iterrows():
        cid = cli["client_id"]
        type_match = (cli["type_voyage_prefere"] == typ)
        budget_ok = budget <= cli.get("budget_max_tnd", budget) * 1.3

        nb_personnes = int(np.clip(rng.poisson(2.2) + 1, 1, 6))
        nb_nuits = int(np.clip(rng.normal(6.5, 2.7), 2, 11))

        hotel_id = rng.choice(dest_htl_map[did])
        flight_id = rng.choice(dest_flt_map[did])
        hotel_price = new_hotels_df.loc[new_hotels_df.hotel_id == hotel_id, "prix_nuit_tnd"].values[0]
        flight_price = new_flights_df.loc[new_flights_df.flight_id == flight_id, "prix_vol_tnd"].values[0]
        montant = round(hotel_price * nb_nuits + flight_price * nb_personnes, 1)

        # date de départ aléatoire 2018-2026, avec un biais léger vers la saison idéale
        year = int(rng.randint(2018, 2027))
        month = int(rng.randint(1, 13))
        day = int(rng.randint(1, 28))
        date_depart = datetime(year, month, day)
        date_reservation = date_depart - timedelta(days=int(rng.randint(20, 90)))
        date_retour = date_depart + timedelta(days=nb_nuits)

        annulee = rng.random() < CANCEL_RATE
        statut = "Annulée" if annulee else "Confirmée"

        if annulee:
            note_satisfaction = np.nan
        else:
            base_note = note_dest if type_match else max(2.2, note_dest - 0.9)
            note_satisfaction = float(np.clip(rng.normal(base_note, 0.35), 1.5, 5.0))

        new_reservations.append({
            "reservation_id": f"{NEW_RES_PREFIX}{res_counter:05d}", "client_id": cid, "destination_id": did,
            "hotel_id": hotel_id, "flight_id": flight_id,
            "date_reservation": date_reservation.strftime("%Y-%m-%d"),
            "date_depart": date_depart.strftime("%Y-%m-%d"),
            "date_retour": date_retour.strftime("%Y-%m-%d"),
            "nb_personnes": nb_personnes, "nb_nuits": nb_nuits, "montant_total_tnd": montant,
            "canal_vente": rng.choice(CANAUX, p=CANAL_P), "statut_reservation": statut,
            "note_satisfaction": note_satisfaction, "source": "généré_v2_enrichissement",
        })
        res_counter += 1

new_res_df = pd.DataFrame(new_reservations)
reservations_enriched = pd.concat([reservations_df, new_res_df], ignore_index=True)
print(f"Réservations : {len(reservations_df)} -> {len(reservations_enriched)} (+{len(new_res_df)})")

# ---------------------------------------------------------------------------
# 4) Sauvegarde
# ---------------------------------------------------------------------------
destinations_enriched.to_csv("destinations_enriched.csv", index=False)
hotels_enriched.to_csv("hotels_enriched.csv", index=False)
flights_enriched.to_csv("flights_enriched.csv", index=False)
reservations_enriched.to_csv("reservations_enriched.csv", index=False)
print("\n✅ Fichiers enrichis sauvegardés.")

# Vérification finale de la couverture
p = preferences_df
d = destinations_enriched
missing = set(p["type_voyage_prefere"].unique()) - set(d["type_voyage"].unique())
print("Types encore manquants après enrichissement :", missing if missing else "AUCUN ✅")
