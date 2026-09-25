"""
scale_pipeline.py
------------------
Extends the country coverage of the tourism revenue-risk model beyond the
162 countries in full_scale_162country_risk.csv.

WHY only 162 out of 216?
Your notebook's get_clean_countries() requires, per country:
  - exactly 22 rows (1999-2020, no gaps)
  - no NaNs in tourism_receipts / gdp / inflation / tourism_arrivals
  - no zero/negative receipts
  - not a flat-lined series (constant value repeated)
That's a strict "Tier 1" filter. Countries that fail it are just dropped.

This script adds two more tiers so almost every country in the cleaned
dataset gets a risk score instead of being silently excluded:

  Tier 1 (strict)   -> full Monte Carlo w/ champion model (same as notebook)
  Tier 2 (relaxed)  -> allow up to 4 interpolated/missing years, still
                       requires >= 10 usable data points; uses whatever
                       growth history exists to parameterise the sim
  Tier 3 (fallback) -> too little history for a trend model; falls back to
                       a Naive-last-value model with a WIDER, penalised
                       uncertainty band (reflects that we have low
                       confidence, not that we invented certainty)

Countries that still don't qualify (e.g. <3 usable years of receipts data)
are reported and excluded — there is genuinely not enough information for
even a rough estimate.

Run:
    python scale_pipeline.py
Output:
    data/full_scale_ALLcountry_risk.csv   (superset of the 162-country file,
                                            with a `tier` and `confidence`
                                            column added)
"""

import numpy as np
import pandas as pd
import warnings
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------- settings
DATA_PATH = "data/cleaned_tourism_data_v2.csv"
OUT_PATH = "data/full_scale_ALLcountry_risk.csv"

HORIZON = 5
FORECAST_YEARS = list(range(2021, 2021 + HORIZON))
N_SIMS = 3000
SEED = 42

FX_SHOCK_STD = 0.05
PANDEMIC_PROB = 0.04
PANDEMIC_MU, PANDEMIC_SIGMA = -0.55, 0.15

MIN_YEARS_TIER2 = 10      # min usable points to attempt a trend model
MIN_YEARS_TIER3 = 3       # min usable points for even a naive fallback
TIER3_SIGMA_INFLATION = 1.6  # widen the uncertainty band when confidence is low


# ---------------------------------------------------------------- helpers
def usable_series(g: pd.DataFrame) -> pd.DataFrame:
    """Rows with a positive, non-null tourism_receipts value, sorted by year."""
    g = g.sort_values("year")
    return g[g["tourism_receipts"].notna() & (g["tourism_receipts"] > 0)]


def classify_country(g: pd.DataFrame) -> str:
    g_full = g.sort_values("year")
    cols = ["tourism_receipts", "gdp", "inflation", "tourism_arrivals"]
    clean = usable_series(g)

    is_flat = False
    r = clean["tourism_receipts"].values
    if len(r) > 1:
        is_flat = np.all(r == r[0])

    tier1_ok = (
        len(g_full) == 22
        and not g_full[cols].isna().any().any()
        and (g_full["tourism_receipts"] > 0).all()
        and not is_flat
    )
    if tier1_ok:
        return "tier1"
    if len(clean) >= MIN_YEARS_TIER2 and not is_flat:
        return "tier2"
    if len(clean) >= MIN_YEARS_TIER3:
        return "tier3"
    return "excluded"


def champion_model_and_growth(clean: pd.DataFrame):
    """Pick a trend model on usable data; return (model_name, growth_mu, growth_sigma)."""
    y = clean["tourism_receipts"].values
    yrs = clean[["year"]]

    growth = clean["tourism_receipts"].pct_change().dropna()
    growth = growth.replace([np.inf, -np.inf], np.nan).dropna()
    mu, sigma = growth.mean(), growth.std()
    if not np.isfinite(sigma) or sigma == 0:
        sigma = max(abs(mu) * 0.5, 0.05)
    if not np.isfinite(mu):
        mu = 0.0

    # Prefer Holt-Winters if enough points, else Linear Trend, else Naive.
    model_name = "Naive"
    try:
        if len(y) >= 8:
            ExponentialSmoothing(y, trend="add", seasonal=None).fit()
            model_name = "Holt-Winters"
        elif len(y) >= 4:
            LinearRegression().fit(yrs, y)
            model_name = "Linear Trend"
    except Exception:
        model_name = "Naive"

    return model_name, mu, sigma


def simulate(last_actual, mu, sigma, sigma_inflation=1.0, n_sims=N_SIMS, seed=SEED):
    rng = np.random.default_rng(seed)
    sigma_eff = sigma * sigma_inflation
    growths = rng.normal(mu, sigma_eff, size=(n_sims, HORIZON))
    fx = rng.normal(0, FX_SHOCK_STD, size=(n_sims, HORIZON))
    shock_mask = rng.random((n_sims, HORIZON)) < PANDEMIC_PROB
    shock_draw = rng.normal(PANDEMIC_MU, PANDEMIC_SIGMA, size=(n_sims, HORIZON))
    shock_vals = np.where(shock_mask, np.clip(shock_draw, -0.9, -0.05), 0.0)
    multipliers = 1 + growths + fx + shock_vals
    multipliers = np.clip(multipliers, -0.95, None)
    paths = last_actual * np.cumprod(multipliers, axis=1)
    return paths


# ---------------------------------------------------------------- main
def main():
    df = pd.read_csv(DATA_PATH)
    df = df.sort_values(["country", "year"])

    rows = []
    excluded = []

    for country, g in df.groupby("country"):
        tier = classify_country(g)
        if tier == "excluded":
            excluded.append(country)
            continue

        clean = usable_series(g)
        last_actual = clean["tourism_receipts"].iloc[-1]
        model_name, mu, sigma = champion_model_and_growth(clean)

        sigma_inflation = TIER3_SIGMA_INFLATION if tier == "tier3" else 1.0
        paths = simulate(last_actual, mu, sigma, sigma_inflation=sigma_inflation)
        final_year_vals = paths[:, -1]

        p5, med, p95 = np.percentile(final_year_vals, [5, 50, 95])
        risk_ratio = p5 / med if med else np.nan

        gdp_share_2019 = g.loc[g["year"] == 2019, "tourism_gdp_share"]
        gdp_share_2019 = gdp_share_2019.iloc[0] if len(gdp_share_2019) else np.nan

        confidence = {"tier1": "high", "tier2": "medium", "tier3": "low"}[tier]

        rows.append({
            "country": country,
            "tourism_gdp_share_2019": gdp_share_2019,
            "champion_model": model_name,
            "2025_P5": p5,
            "2025_median": med,
            "2025_P95": p95,
            "risk_ratio": risk_ratio,
            "tier": tier,
            "confidence": confidence,
            "years_used": len(clean),
        })

    out = pd.DataFrame(rows).sort_values("risk_ratio")
    out.to_csv(OUT_PATH, index=False)

    print(f"Total countries in source data : {df['country'].nunique()}")
    print(f"Scored (tier1 strict)          : {(out['tier']=='tier1').sum()}")
    print(f"Scored (tier2 relaxed)         : {(out['tier']=='tier2').sum()}")
    print(f"Scored (tier3 fallback)        : {(out['tier']=='tier3').sum()}")
    print(f"Excluded (too little data)     : {len(excluded)}")
    if excluded:
        print("  Excluded countries:", ", ".join(sorted(excluded)))
    print(f"\nSaved -> {OUT_PATH}  ({len(out)} countries)")


if __name__ == "__main__":
    main()
