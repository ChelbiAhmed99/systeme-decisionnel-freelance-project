"""
Moteur de recommandation TravelBI (sans interface graphique)
============================================================
Reproduit à l'identique le modèle HYBRIDE entraîné dans le notebook (Section 10) :
    score = w1*Content-Based + w2*Matrix-Factorization + w3*Booster + w4*Popularité   (clippé sur [0, 5])
Fonctionne pour un client EXISTANT (embeddings MF connus, destinations déjà réservées exclues) et pour un
NOUVEAU client (cold-start : profil déclaré uniquement ; la composante MF se limite au biais de la destination).

Il lit le dossier exporté par la Section 15 du notebook : models/ et data/.
Contrôle sans interface :  python moteur_reco.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCORE_MAX = 5.0


def _make_predictor(spec, models_dir):
    """Recharge un booster depuis son format natif (robuste aux changements de version)."""
    kind, path = spec["type"], Path(models_dir) / spec["file"]
    if kind == "lightgbm":
        import lightgbm as lgb
        booster = lgb.Booster(model_file=str(path))
        return lambda X: np.asarray(booster.predict(X))
    if kind == "xgboost":
        import xgboost as xgb
        model = xgb.XGBRegressor()
        model.load_model(str(path))
        return lambda X: np.asarray(model.predict(X))
    if kind == "catboost":
        from catboost import CatBoostRegressor
        model = CatBoostRegressor()
        model.load_model(str(path))
        return lambda X: np.asarray(model.predict(X))
    if kind == "joblib":  # repli générique (tout objet exposant .predict)
        import joblib
        model = joblib.load(path)
        return lambda X: np.asarray(model.predict(X))
    raise ValueError(f"Type de booster inconnu : {kind}")


class RecommenderEngine:
    def __init__(self, app_dir):
        app_dir = Path(app_dir)
        models_dir = app_dir / "models"
        with open(models_dir / "artifacts_meta.json", encoding="utf-8") as f:
            self.meta = json.load(f)
        m = self.meta

        self.client_ids = list(m["client_id_list"])
        self.dest_ids = list(m["dest_id_list"])
        self.types = list(m["mlb_types"])
        self.acts = list(m["mlb_acts"])
        self.client_feat_cols = list(m["client_feat_cols"])
        self.dest_feat_cols = list(m["dest_feat_cols"])
        self.sup_columns = list(m["sup_columns"])
        self.weights = tuple(float(w) for w in m["hybrid_weights"])
        self.k_eval = int(m.get("k_eval", 7))
        self.best_booster_name = m.get("best_booster_name", "?")
        self.best_model_name = m.get("best_model_name", "Hybride")

        self._predictors = [_make_predictor(s, models_dir) for s in m["booster_specs"]]

        mf = np.load(models_dir / "mf_embeddings.npz")
        self.P, self.Q = mf["P"], mf["Q"]
        self.b_u, self.b_i, self.mu = mf["b_u"], mf["b_i"], float(mf["mu"])

        cv = np.load(models_dir / "content_vectors.npz")
        self.client_vectors, self.dest_vectors = cv["client_vectors"], cv["dest_vectors"]

        self.clients = pd.read_csv(models_dir / "client_features_for_app.csv").set_index("client_id")
        self.clients = self.clients.loc[self.client_ids]
        self.dests = pd.read_csv(models_dir / "destination_features_for_app.csv").set_index("destination_id")
        self.dests = self.dests.loc[self.dest_ids]

        inter = pd.read_csv(app_dir / "data" / "interactions.csv")
        self.booked = inter.groupby("client_id")["destination_id"].apply(set).to_dict()
        self.client_idx = {c: i for i, c in enumerate(self.client_ids)}

    # ------------------------------------------------------------------ profils
    def profile_of_client(self, client_id):
        """Profil d'un client existant, tel que vu par le modèle."""
        row = self.clients.loc[client_id]
        prof = {c: float(row[c]) for c in self.client_feat_cols}
        prof["type_voyage_prefere"] = str(row["type_voyage_prefere"])
        prof["activites_preferees"] = str(row["activites_preferees"])
        return prof

    def new_client_profile(self, age, revenu_mensuel_tnd, type_voyage_prefere, activites, budget_max_tnd):
        """Profil d'un nouveau client (aucun historique : mêmes valeurs par défaut que le notebook)."""
        defaults = {
            "age": age, "revenu_mensuel_tnd": revenu_mensuel_tnd, "frequence": 0.0, "montant_moyen": 0.0,
            "recence_jours": 9999.0, "taux_annulation": 0.0, "budget_max_tnd": budget_max_tnd,
        }
        prof = {c: float(defaults.get(c, 0.0)) for c in self.client_feat_cols}
        prof["budget_max_tnd"] = float(budget_max_tnd)
        prof["type_voyage_prefere"] = str(type_voyage_prefere)
        prof["activites_preferees"] = ";".join(activites)
        return prof

    def _profile_vector(self, prof):
        v_type = np.zeros(len(self.types))
        if prof["type_voyage_prefere"] in self.types:
            v_type[self.types.index(prof["type_voyage_prefere"])] = 1.0
        v_act = np.zeros(len(self.acts))
        for a in str(prof["activites_preferees"]).split(";"):
            if a in self.acts:
                v_act[self.acts.index(a)] = 1.0
        budget_norm = np.clip(prof["budget_max_tnd"] / 20000.0, 0, 1)
        return np.concatenate([v_type, v_act, [budget_norm]])

    # ------------------------------------------------------------------ scoring
    def _cosine(self, cvec):
        norms = np.linalg.norm(self.dest_vectors, axis=1) * np.linalg.norm(cvec)
        dots = self.dest_vectors @ cvec
        return np.divide(dots, norms, out=np.zeros_like(dots), where=norms > 0)

    def _booster_scores(self, prof, sims):
        n = len(self.dest_ids)
        data = {c: np.full(n, float(prof[c])) for c in self.client_feat_cols}
        for c in self.dest_feat_cols:
            data[c] = self.dests[c].to_numpy(dtype=float)
        pref_acts = set(str(prof["activites_preferees"]).split(";"))
        data["content_similarity"] = sims
        data["type_match"] = (self.dests["type_voyage"].to_numpy() == prof["type_voyage_prefere"]).astype(float)
        data["activity_overlap"] = np.array(
            [len(pref_acts & set(str(a).split(";"))) for a in self.dests["activites_disponibles"]], dtype=float)
        data["budget_ratio"] = self.dests["budget_moyen_tnd"].to_numpy(dtype=float) / max(prof["budget_max_tnd"], 1.0)
        X = pd.DataFrame(data)[self.sup_columns]
        # comme dans le notebook : chaque booster est clippé sur [0, 5] AVANT la moyenne (cas « Ensemble »)
        return np.mean([np.clip(p(X), 0, SCORE_MAX) for p in self._predictors], axis=0)

    def _explain(self, prof, did):
        d = self.dests.loc[did]
        raisons = []
        if prof["type_voyage_prefere"] == d["type_voyage"]:
            raisons.append(f"correspond à votre type de voyage préféré ({d['type_voyage']})")
        communes = set(str(prof["activites_preferees"]).split(";")) & set(str(d["activites_disponibles"]).split(";"))
        if communes:
            raisons.append(f"propose des activités que vous aimez ({', '.join(sorted(communes)[:2])})")
        if d["budget_moyen_tnd"] <= prof["budget_max_tnd"] * 1.1:
            raisons.append("s'inscrit dans votre budget habituel")
        if d["popularite_score"] >= 70:
            raisons.append("est une destination très plébiscitée par nos clients")
        if d["satisfaction_moyenne"] >= 4.2:
            raisons.append(f"affiche une excellente satisfaction client ({d['satisfaction_moyenne']:.1f}/5)")
        if not raisons:
            raisons.append("a été identifiée comme pertinente par le modèle hybride "
                           "(similarité de profil + comportement collectif)")
        return " ; ".join(raisons)

    def _recommend(self, prof, client_index, exclude, n):
        w = self.weights
        cvec = self.client_vectors[client_index] if client_index is not None else self._profile_vector(prof)
        sims = self._cosine(cvec)
        cb = np.clip(sims, 0, 1) * SCORE_MAX
        if client_index is not None:
            mf = self.mu + self.b_u[client_index] + self.b_i + self.Q @ self.P[client_index]
        else:  # cold-start : pas d'embedding client -> biais global + biais destination
            mf = self.mu + self.b_i
        mf = np.clip(mf, 0, SCORE_MAX)
        boost = self._booster_scores(prof, sims)
        pop = self.dests["popularite_score"].to_numpy(dtype=float) / 100.0 * SCORE_MAX
        hybrid = np.clip(w[0] * cb + w[1] * mf + w[2] * boost + w[3] * pop, 0, SCORE_MAX)

        out = pd.DataFrame({
            "destination_id": self.dest_ids,
            "nom_destination": self.dests["nom_destination"].to_numpy(),
            "type_voyage": self.dests["type_voyage"].to_numpy(),
            "pays_continent": self.dests["pays_continent"].to_numpy(),
            "budget_moyen_tnd": self.dests["budget_moyen_tnd"].to_numpy(),
            "score": hybrid,
            "s_content": cb, "s_collab": mf, "s_booster": boost, "s_popularite": pop,
            "contrib_content": w[0] * cb, "contrib_collab": w[1] * mf,
            "contrib_booster": w[2] * boost, "contrib_popularite": w[3] * pop,
        })
        out = out[~out["destination_id"].isin(exclude)]
        out = out.sort_values("score", ascending=False).head(n).reset_index(drop=True)
        out.insert(0, "rang", np.arange(1, len(out) + 1))
        out["explication"] = [self._explain(prof, d) for d in out["destination_id"]]
        return out

    # ------------------------------------------------------------------ API publique
    def recommend_for_client(self, client_id, n=5):
        if client_id not in self.client_idx:
            raise ValueError(f"Client inconnu : {client_id}")
        return self._recommend(self.profile_of_client(client_id), self.client_idx[client_id],
                               self.booked.get(client_id, set()), n)

    def recommend_for_profile(self, profile, n=5):
        return self._recommend(profile, None, set(), n)

    def client_label(self, client_id):
        r = self.clients.loc[client_id]
        return f"{client_id} — {r.get('prenom', '')} {r.get('nom', '')} · {r.get('segment_latent', '')}".replace("  ", " ")


def selfcheck(app_dir, engine=None):
    """Compare le moteur aux recommandations de référence exportées par le notebook (data/reference_recos.csv).
    Retourne (ok, message)."""
    ref_path = Path(app_dir) / "data" / "reference_recos.csv"
    if not ref_path.exists():
        return False, "data/reference_recos.csv introuvable : relancez la section 15 du notebook."
    engine = engine or RecommenderEngine(app_dir)
    ref = pd.read_csv(ref_path)
    same_top, max_gap, n_clients, k = 0, 0.0, 0, 0
    for cid, grp in ref.groupby("client_id"):
        grp = grp.sort_values("rang")
        k = len(grp)
        got = engine.recommend_for_client(cid, n=k)
        same_top += int(got["destination_id"].tolist() == grp["destination_id"].tolist())
        max_gap = max(max_gap, float(np.abs(got["score"].round(2).to_numpy() - grp["score"].to_numpy()).max()))
        n_clients += 1
    ok = n_clients > 0 and same_top == n_clients and max_gap <= 0.011
    return ok, (f"Top-{k} identique au notebook pour {same_top}/{n_clients} clients, "
                f"écart de score maximal {max_gap:.3f}.")


if __name__ == "__main__":
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    ok, msg = selfcheck(base)
    print(("OK  " if ok else "ÉCART  ") + msg)
    sys.exit(0 if ok else 1)
