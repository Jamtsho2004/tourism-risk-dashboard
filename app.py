"""
Tourism Revenue Risk Dashboard
--------------------------------
Streamlit dashboard for the tourism-dependency / revenue-risk analysis.

Run locally:
    streamlit run app.py

Data expected in ./data/:
    cleaned_tourism_data_v2.csv        (1999-2020 panel, all countries)
    full_scale_162country_risk.csv     (strict-tier risk model, from notebook)
    full_scale_ALLcountry_risk.csv     (optional - wider coverage, from scale_pipeline.py)
    multi_country_risk_comparison.csv  (Japan/Mexico/Thailand/Croatia case study)
    thailand_revenue_risk_forecast.csv (Thailand year-by-year fan chart data)
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Tourism Revenue Risk Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"

# --------------------------------------------------------------------------
# Academic theme: fonts, color palette, hover effects
# --------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {
    --navy: #1B2A4A;
    --navy-light: #2E4374;
    --gold: #B08D57;
    --paper: #FAF9F6;
    --ink: #262730;
    --muted: #5B6472;
    --border: #E3E1DA;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
}

h1, h2, h3, .kpi-value, .app-title {
    font-family: 'Source Serif 4', Georgia, serif !important;
}

/* App background */
.stApp {
    background-color: var(--paper);
}

/* Header banner */
.app-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
    padding: 2.2rem 2.5rem;
    border-radius: 10px;
    margin-bottom: 1.6rem;
    box-shadow: 0 4px 18px rgba(27,42,74,0.18);
}
.app-title {
    color: #FFFFFF;
    font-size: 2.1rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
    letter-spacing: 0.2px;
}
.app-subtitle {
    color: #C9D2E3;
    font-family: 'Inter', sans-serif;
    font-size: 0.98rem;
    line-height: 1.5;
    max-width: 900px;
    margin: 0;
}
.app-kicker {
    color: var(--gold);
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* KPI cards */
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.6rem; flex-wrap: wrap; }
.kpi-card {
    flex: 1 1 200px;
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-left-color 0.18s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(27,42,74,0.12);
    border-left-color: var(--navy);
}
.kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1.15;
}
.kpi-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 0.25rem;
}

/* Section labels */
.section-kicker {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.15rem;
}
.section-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--navy);
    margin-top: 0;
    margin-bottom: 0.8rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--muted);
    padding: 10px 18px;
    border-radius: 8px 8px 0 0;
    transition: background-color 0.15s ease, color 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { background-color: #EFF2F8; color: var(--navy); }
.stTabs [aria-selected="true"] { color: var(--navy) !important; border-bottom: 3px solid var(--gold) !important; }

/* Dataframe / table polish */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h1 { font-family: 'Source Serif 4', Georgia, serif; color: var(--navy); }

/* Card-style containers for chart blocks */
.chart-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem 0.6rem 1.4rem;
    margin-bottom: 1.2rem;
    transition: box-shadow 0.18s ease;
}
.chart-card:hover { box-shadow: 0 8px 22px rgba(27,42,74,0.08); }

/* Footer */
.app-footer {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: var(--muted);
    text-align: center;
    padding: 1.4rem 0 0.6rem 0;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


def kpi_card(label, value, sub=""):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def section_header(kicker, title):
    st.markdown(
        f'<div class="section-kicker">{kicker}</div>'
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Data loading (cached)
# --------------------------------------------------------------------------
@st.cache_data
def load_panel():
    path = os.path.join(DATA_DIR, "cleaned_tourism_data_v2.csv")
    return pd.read_csv(path)


@st.cache_data
def load_risk():
    """Prefer the wider-coverage file (from scale_pipeline.py) if present,
    otherwise fall back to the original 162-country notebook output."""
    wide_path = os.path.join(DATA_DIR, "full_scale_ALLcountry_risk.csv")
    strict_path = os.path.join(DATA_DIR, "full_scale_162country_risk.csv")

    if os.path.exists(wide_path):
        df = pd.read_csv(wide_path)
        source = "Scaled model (Tier 1/2/3) — run scale_pipeline.py to refresh"
    else:
        df = pd.read_csv(strict_path)
        df["tier"] = "tier1"
        df["confidence"] = "high"
        source = "Strict model (162 countries, from notebook)"
    return df, source


@st.cache_data
def load_case_study():
    return pd.read_csv(os.path.join(DATA_DIR, "multi_country_risk_comparison.csv"))


@st.cache_data
def load_thailand_forecast():
    return pd.read_csv(os.path.join(DATA_DIR, "thailand_revenue_risk_forecast.csv"))


panel = load_panel()
risk, risk_source = load_risk()
case_study = load_case_study()
thailand_fc = load_thailand_forecast()

# country -> ISO3 + region lookup, for the map and filters
lookup = panel.drop_duplicates("country")[["country", "country_code", "region"]]
risk = risk.merge(lookup, on="country", how="left")

CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}
if "confidence" not in risk.columns:
    risk["confidence"] = "high"
if "tier" not in risk.columns:
    risk["tier"] = "tier1"


# --------------------------------------------------------------------------
# Sidebar controls
# --------------------------------------------------------------------------
st.sidebar.title("🌍 Tourism Revenue Risk")
st.sidebar.caption(risk_source)

regions = sorted(risk["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

conf_levels = sorted(risk["confidence"].dropna().unique().tolist(),
                      key=lambda c: CONFIDENCE_ORDER.get(c, 9))
selected_conf = st.sidebar.multiselect(
    "Model confidence", conf_levels, default=conf_levels,
    help="high = strict Tier-1 filter passed · medium = relaxed Tier-2 · "
         "low = Tier-3 fallback with widened uncertainty",
)

min_share, max_share = float(risk["tourism_gdp_share_2019"].min()), float(risk["tourism_gdp_share_2019"].max())
share_range = st.sidebar.slider(
    "Tourism share of GDP, 2019 (%)",
    min_value=0.0, max_value=round(max_share, 1),
    value=(0.0, round(max_share, 1)),
)

filtered = risk[
    risk["region"].isin(selected_regions)
    & risk["confidence"].isin(selected_conf)
    & risk["tourism_gdp_share_2019"].between(*share_range)
].copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Showing **{len(filtered)}** of {len(risk)} scored countries "
    f"({risk['country'].nunique()} total in dataset)."
)

# --------------------------------------------------------------------------
# Header + KPIs
# --------------------------------------------------------------------------
st.markdown(f"""
<div class="app-header">
    <div class="app-kicker">Quantitative Tourism Economics · Monte Carlo Risk Model</div>
    <div class="app-title">Tourism Revenue Risk Dashboard</div>
    <p class="app-subtitle">
        Projected 2025 revenue-at-risk by country, estimated from a Monte Carlo simulation
        over champion time-series models (Naive · Linear Trend · Holt-Winters · ARIMA)
        fitted on 1999–2020 tourism receipts, with fat-tail shocks for currency
        volatility and low-probability demand disruptions.
    </p>
</div>
""", unsafe_allow_html=True)

most_fragile = filtered.nsmallest(1, "risk_ratio")
most_resilient = filtered.nlargest(1, "risk_ratio")

kpi_html = '<div class="kpi-row">'
kpi_html += kpi_card("Countries Scored", f"{len(filtered):,}", f"of {risk['country'].nunique()} in dataset")
kpi_html += kpi_card(
    "Most Fragile",
    most_fragile["country"].values[0] if len(most_fragile) else "—",
    f"risk ratio {most_fragile['risk_ratio'].values[0]:.2f}" if len(most_fragile) else "No data in view",
)
kpi_html += kpi_card(
    "Most Resilient",
    most_resilient["country"].values[0] if len(most_resilient) else "—",
    f"risk ratio {most_resilient['risk_ratio'].values[0]:.2f}" if len(most_resilient) else "No data in view",
)
kpi_html += kpi_card(
    "Median 2025 Revenue",
    f"${filtered['2025_median'].median():,.0f}",
    "across countries in view",
)
kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_map, tab_country, tab_compare, tab_data = st.tabs(
    ["Global Map", "Country Deep Dive", "Compare Countries", "Data & Methodology"]
)

# ---- Tab 1: global choropleth -------------------------------------------
with tab_map:
    section_header("Figure 1", "Global Distribution of Revenue Risk")
    c1, c2 = st.columns([3, 1])
    with c2:
        color_metric = st.radio(
            "Color by",
            ["risk_ratio", "tourism_gdp_share_2019", "2025_median"],
            format_func=lambda x: {
                "risk_ratio": "Risk ratio (P5 / median) — lower = riskier",
                "tourism_gdp_share_2019": "Tourism dependence (% GDP, 2019)",
                "2025_median": "Projected 2025 median revenue",
            }[x],
        )
        color_scale = "RdYlGn" if color_metric == "risk_ratio" else "OrRd"

    with c1:
        fig = px.choropleth(
            filtered,
            locations="country_code",
            color=color_metric,
            hover_name="country",
            hover_data={
                "champion_model": True,
                "confidence": True,
                "risk_ratio": ":.2f",
                "tourism_gdp_share_2019": ":.1f",
                "country_code": False,
            },
            color_continuous_scale=color_scale,
            projection="natural earth",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=520)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Table 1", "Most Fragile Economies (Current Filter)")
    st.dataframe(
        filtered.nsmallest(10, "risk_ratio")[
            ["country", "region", "tourism_gdp_share_2019", "champion_model", "risk_ratio", "confidence"]
        ].reset_index(drop=True),
        use_container_width=True,
    )

# ---- Tab 2: country deep dive --------------------------------------------
with tab_country:
    section_header("Figure 2", "Country-Level Forecast & Uncertainty Band")
    country_list = sorted(filtered["country"].unique().tolist())
    if not country_list:
        st.warning("No countries match the current filters.")
    else:
        default_idx = country_list.index("Thailand") if "Thailand" in country_list else 0
        sel_country = st.selectbox("Select a country", country_list, index=default_idx)

        row = risk[risk["country"] == sel_country].iloc[0]
        hist = panel[panel["country"] == sel_country].sort_values("year")

        c1, c2, c3 = st.columns(3)
        c1.metric("Champion model", row["champion_model"])
        c2.metric("Tourism share of GDP (2019)", f"{row['tourism_gdp_share_2019']:.1f}%")
        c3.metric("Model confidence", row["confidence"])

        # Fan chart: historical + P5/median/P95 projection.
        # Use the real Thailand fan-chart CSV if that's the selected country
        # and it has full year-by-year percentiles; otherwise draw a
        # simplified 2-point fan from the summary row (last actual -> 2025).
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist["year"], y=hist["tourism_receipts"],
            mode="lines+markers", name="Historical (actual)", line=dict(color="black"),
        ))

        if sel_country == "Thailand" and not thailand_fc.empty:
            fig.add_trace(go.Scatter(
                x=thailand_fc["year"], y=thailand_fc["P50_median"],
                mode="lines+markers", name="Median simulated path", line=dict(color="steelblue"),
            ))
            fig.add_trace(go.Scatter(
                x=list(thailand_fc["year"]) + list(thailand_fc["year"])[::-1],
                y=list(thailand_fc["P95"]) + list(thailand_fc["P5"])[::-1],
                fill="toself", fillcolor="rgba(70,130,180,0.15)",
                line=dict(color="rgba(255,255,255,0)"), name="90% interval (P5-P95)",
                showlegend=True,
            ))
        else:
            last_year = hist["year"].max()
            last_val = hist.loc[hist["year"] == last_year, "tourism_receipts"].values[0]
            fig.add_trace(go.Scatter(
                x=[last_year, 2025], y=[last_val, row["2025_median"]],
                mode="lines+markers", name="Median 2025 projection", line=dict(color="steelblue"),
            ))
            fig.add_trace(go.Scatter(
                x=[last_year, 2025, 2025, last_year],
                y=[last_val, row["2025_P95"], row["2025_P5"], last_val],
                fill="toself", fillcolor="rgba(70,130,180,0.15)",
                line=dict(color="rgba(255,255,255,0)"), name="90% interval (P5-P95)",
            ))

        fig.update_layout(
            title=f"{sel_country}: tourism receipts, history + 2025 risk range",
            xaxis_title="Year", yaxis_title="Tourism receipts (US$)",
            height=480, legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            f"2025 projection — P5: ${row['2025_P5']:,.0f} · "
            f"Median: ${row['2025_median']:,.0f} · "
            f"P95: ${row['2025_P95']:,.0f} · "
            f"Risk ratio (P5/median): {row['risk_ratio']:.2f}"
        )

# ---- Tab 3: compare countries ---------------------------------------------
with tab_compare:
    section_header("Figure 3", "Case Study — Japan, Mexico, Thailand, Croatia")
    st.caption("Ordered low to high tourism dependence, from the original multi-country comparison.")

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        x=case_study["country"], y=case_study["risk_ratio_P5_over_median"],
        marker_color="steelblue", name="Risk ratio (P5/median)",
    ))
    fig_cmp.update_layout(
        yaxis_title="2025 P5 / Median (lower = worse downside risk)",
        height=380,
    )
    st.plotly_chart(fig_cmp, use_container_width=True)
    st.dataframe(case_study, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Figure 4", "Custom Country Comparison")
    multi_sel = st.multiselect(
        "Pick countries to compare (from the current filtered set)",
        sorted(filtered["country"].unique().tolist()),
        default=[c for c in ["Thailand", "Japan", "Mexico"] if c in filtered["country"].values][:3],
    )
    if multi_sel:
        sub = filtered[filtered["country"].isin(multi_sel)]
        fig2 = px.scatter(
            sub, x="tourism_gdp_share_2019", y="risk_ratio",
            size="2025_median", color="country", hover_name="country",
            labels={
                "tourism_gdp_share_2019": "Tourism share of GDP (2019, %)",
                "risk_ratio": "Risk ratio (P5/median)",
            },
        )
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, use_container_width=True)

# ---- Tab 4: data + methodology ---------------------------------------------
with tab_data:
    section_header("Table 2", "Full Scored Dataset (Current Filters)")
    st.dataframe(filtered.sort_values("risk_ratio"), use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_tourism_risk.csv",
        mime="text/csv",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Appendix", "Methodology Summary")
    st.markdown(
        """
- **Source data:** World Bank-style tourism & economic indicators, 1999–2020, per country.
- **Champion model selection:** Naive, Linear Trend, Holt-Winters, and ARIMA(1,1,1)
  are backtested on a normal-times holdout (train ≤2016, test 2017–2019); the
  best performer per country is kept as its "champion model" for the 2025 baseline.
- **Monte Carlo risk simulation:** 3,000–10,000 simulated 5-year paths (2021–2025)
  per country, combining historical growth volatility, FX shocks, and a small
  probability (4%/year) of a pandemic-scale demand shock.
- **Risk ratio** = 2025 P5 (5th percentile, i.e. bad-case) revenue ÷ 2025 median
  revenue. Lower = a worse worst-case relative to the expected case.
- **Coverage tiers** (only present if you've run `scale_pipeline.py`):
  - *Tier 1 / high confidence* — full 22-year clean series, strict notebook filter.
  - *Tier 2 / medium confidence* — 10+ usable years, some gaps interpolated.
  - *Tier 3 / low confidence* — 3+ usable years only; simplified Naive model with
    a widened uncertainty band to reflect lower confidence.

**Full research notebook:** `notebooks/Mini_Project_Part2_Modeling.ipynb`
(included in this repository) contains the complete model backtesting,
champion-model selection, and Monte Carlo simulation code behind this dashboard.
"""
    )

# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        Tourism Revenue Risk Dashboard · Monte Carlo simulation over 1999–2020 tourism receipts ·
        Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
