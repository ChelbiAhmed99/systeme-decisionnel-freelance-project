"""
Indicateurs du tableau de bord TravelBI (sans interface graphique)
==================================================================
Calculés à partir de data/fact_reservations.csv (exporté par le notebook, sections 14-15),
avec les mêmes définitions que les KPI Power BI du notebook :
  - chiffre d'affaires = réservations « Confirmée » uniquement ;
  - taux d'annulation  = réservations « Annulée » / toutes les réservations.
"""
from pathlib import Path

import numpy as np
import pandas as pd

CONFIRMEE, ANNULEE = "Confirmée", "Annulée"


def charger(app_dir):
    """Retourne le DataFrame des réservations, ou lève FileNotFoundError."""
    path = Path(app_dir) / "data" / "fact_reservations.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path.relative_to(Path(app_dir))} introuvable (section 15 du notebook).")
    f = pd.read_csv(path)
    f["annee"] = pd.to_numeric(f["annee"], errors="coerce").astype("Int64")
    f["mois"] = pd.to_numeric(f["mois"], errors="coerce").astype("Int64")
    f["montant_total_tnd"] = pd.to_numeric(f["montant_total_tnd"], errors="coerce").fillna(0.0)
    return f


def annees(f):
    return sorted(int(a) for a in f["annee"].dropna().unique())


def _filtre(f, annee):
    return f if annee is None else f[f["annee"] == annee]


def kpis(f, annee=None):
    s = _filtre(f, annee)
    conf = s[s["statut_reservation"] == CONFIRMEE]
    n = len(s)
    out = {
        "ca": float(conf["montant_total_tnd"].sum()),
        "reservations": n,
        "panier_moyen": float(conf["montant_total_tnd"].mean()) if len(conf) else np.nan,
        "taux_annulation": (s["statut_reservation"] == ANNULEE).mean() * 100 if n else np.nan,
        "satisfaction": float(conf["note_satisfaction"].mean()) if len(conf) else np.nan,
        "clients_actifs": int(s["client_id"].nunique()),
    }
    # variation vs année précédente (uniquement si une année est choisie et que la précédente existe)
    out["variation"] = {}
    if annee is not None and (annee - 1) in annees(f):
        prev = kpis(f, annee - 1)
        for k in ("ca", "reservations", "panier_moyen", "clients_actifs"):
            if prev[k] and not np.isnan(prev[k]):
                out["variation"][k] = (out[k] / prev[k] - 1) * 100
        for k in ("taux_annulation", "satisfaction"):          # écarts en points
            if not np.isnan(prev[k]) and not np.isnan(out[k]):
                out["variation"][k] = out[k] - prev[k]
    return out


def ca_mensuel(f, annee=None, nb_mois=24):
    conf = f[f["statut_reservation"] == CONFIRMEE]
    g = conf.groupby(["annee", "mois"])["montant_total_tnd"].sum()
    if annee is not None:
        return pd.Series([float(g.get((annee, m), 0.0)) for m in range(1, 13)],
                         index=[pd.Period(year=annee, month=m, freq="M") for m in range(1, 13)])
    if g.empty:
        return pd.Series(dtype=float)
    idx = pd.PeriodIndex([pd.Period(year=int(a), month=int(m), freq="M") for a, m in g.index])
    s = pd.Series(g.values, index=idx).sort_index()
    s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="M"), fill_value=0.0)
    return s.tail(nb_mois)


def top_destinations(f, annee=None, n=8):
    s = _filtre(f, annee)
    return (s[s["statut_reservation"] == CONFIRMEE].groupby("nom_destination")["montant_total_tnd"]
            .sum().sort_values(ascending=False).head(n))


def par_canal(f, annee=None):
    s = _filtre(f, annee)
    g = s.groupby("canal_vente").agg(
        ca=("montant_total_tnd", lambda x: x[s.loc[x.index, "statut_reservation"] == CONFIRMEE].sum()),
        reservations=("reservation_id", "count"),
        annulees=("statut_reservation", lambda x: (x == ANNULEE).sum()))
    g["taux_annulation"] = g["annulees"] / g["reservations"] * 100
    return g.sort_values("ca", ascending=False)


def par_type(f, annee=None):
    s = _filtre(f, annee)
    return (s[s["statut_reservation"] == CONFIRMEE].groupby("type_voyage")["montant_total_tnd"]
            .sum().sort_values(ascending=False))


if __name__ == "__main__":
    import sys
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    fr = charger(base)
    a = annees(fr)[-1]
    print(a, kpis(fr, a))
    print(par_canal(fr, a))
