import json

import pandas as pd
from sklearn.inspection import permutation_importance

from .config import MODEL_INFO, TARGET


def features() -> list:
    return json.loads(MODEL_INFO.read_text())["feature_names"]


def importance(model, df, n=3000) -> pd.Series:
    """How much the average error grows (GB) when a feature is shuffled. Bigger means more important."""
    d = df.dropna(subset=[TARGET])
    d = d.sample(min(n, len(d)), random_state=0)
    cols = features()
    r = permutation_importance(model, d[cols], d[TARGET], scoring="neg_mean_absolute_error",
                               n_repeats=3, random_state=0)
    return pd.Series(r.importances_mean, index=cols).sort_values(ascending=False)


# ---- SHAP: how each feature moved one forecast away from the average forecast ----

def shap_values(model, df, n=300, background=20) -> dict:
    """SHAP values (GB) for a sample of rows. Works with the saved pipeline as it is: text columns are turned into
    codes for SHAP and back into text before the model sees them, so the model and its forecasts are unchanged.
    Returns {"values": DataFrame, "data": DataFrame (original feature values), "base": float, "forecast": Series}."""
    import numpy as np
    import shap

    cols = features()
    d = df.dropna(subset=[TARGET])[cols] if TARGET in df else df[cols]
    X = d.sample(min(n, len(d)), random_state=1)
    bg = d.sample(min(background, len(d)), random_state=0)
    cat = [c for c in cols if not pd.api.types.is_numeric_dtype(d[c])]
    cats = {c: list(pd.Index(d[c].astype(str).unique())) for c in cat}

    def enc(x):
        x = x.copy()
        for c in cat:
            x[c] = pd.Categorical(x[c].astype(str), categories=cats[c]).codes
        return x.astype(float)

    def predict(a):
        x = pd.DataFrame(a, columns=cols)
        for c in cat:
            x[c] = np.asarray(cats[c], dtype=object)[np.clip(np.rint(x[c]).astype(int), 0, len(cats[c]) - 1)]
        return np.clip(model.predict(x), 0, None)

    ex = shap.Explainer(predict, enc(bg).values, algorithm="permutation", seed=0)
    sv = ex(enc(X).values, max_evals=2 * len(cols) + 1, silent=True)
    return {"values": pd.DataFrame(sv.values, index=X.index, columns=cols), "data": X,
            "base": float(np.mean(sv.base_values)), "forecast": pd.Series(predict(enc(X).values), index=X.index)}


def shap_summary(res) -> pd.DataFrame:
    """One row per feature: average size of the effect (GB), and which way it pushes. Sorted by size."""
    import numpy as np
    v, x = res["values"], res["data"]
    rows = []
    for c in v.columns:
        size = float(v[c].abs().mean())
        if pd.api.types.is_numeric_dtype(x[c]) and x[c].nunique() > 2 and v[c].std() > 0:
            r = float(np.corrcoef(x[c].rank(), v[c])[0, 1])
            way = "up" if r > 0.2 else "down" if r < -0.2 else "mixed"
            note = {"up": "Higher values raise the forecast.", "down": "Higher values lower the forecast.",
                    "mixed": "No steady direction. The effect depends on other features."}[way]
        else:
            g = v[c].groupby(x[c].astype(str)).mean().sort_values()
            way = "category"
            note = (f"Raises the forecast most for {g.index[-1].replace('_', ' ')} ({g.iloc[-1]:+.2f} GB) and lowers it "
                    f"most for {g.index[0].replace('_', ' ')} ({g.iloc[0]:+.2f} GB).") if len(g) > 1 else "Only one value in this data."
        rows.append({"feature": c, "size": size, "way": way, "note": note})
    return pd.DataFrame(rows).sort_values("size", ascending=False).reset_index(drop=True)


def shap_sentence(summary, base) -> str:
    top = summary.iloc[0]
    tot = summary["size"].sum() or 1
    share = top["size"] / tot
    return (f"{top['feature'].replace('_', ' ')} matters most. On average it moves a forecast by {top['size']:.2f} GB, "
            f"about {share:.0%} of all feature effects. {top['note']} The average forecast in this sample is {base:.1f} GB, "
            "and every feature either adds to or takes away from that number.")


def shap_row_text(res, idx, k=3) -> str:
    """Plain-language reason for one forecast: what raised it, what lowered it."""
    v = res["values"].loc[idx].sort_values()
    x = res["data"].loc[idx]
    fmt = lambda c: (f"{x[c]:.2f}" if pd.api.types.is_number(x[c]) else str(x[c]).replace("_", " "))
    up = [f"{c.replace('_', ' ')} = {fmt(c)} ({val:+.2f} GB)" for c, val in v[::-1].head(k).items() if val > 0.005]
    down = [f"{c.replace('_', ' ')} = {fmt(c)} ({val:+.2f} GB)" for c, val in v.head(k).items() if val < -0.005]
    out = f"The forecast is {res['forecast'][idx]:.1f} GB, against an average of {res['base']:.1f} GB."
    if up:
        out += " Pushing it up: " + "; ".join(up) + "."
    if down:
        out += " Pulling it down: " + "; ".join(down) + "."
    return out
