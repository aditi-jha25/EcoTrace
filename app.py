import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="EcoTrace Dashboard", page_icon="🌿", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(180deg, #f3faf6 0%, #eff7ff 100%);
            color: #103b2d;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: #0d2d22;
            color: #edfdf4;
        }

        .stSelectbox label, .stMultiSelect label, .stSlider label {
            color: #eaf7ee;
            font-weight: 600;
        }

        .stMetric {
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(18,94,65,0.12);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 8px 20px rgba(35, 79, 63, 0.06);
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #103b2d !important;
            font-weight: 800;
        }

        .stMetric [data-testid="stMetricLabel"] {
            color: #55776d !important;
        }

        .kpi-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08rem;
            color: #55776d;
            font-weight: 700;
        }

        .main-header {
            font-size: 2.4rem;
            font-weight: 800;
            color: #113b2d;
            margin-bottom: 0.2rem;
        }

        .sub-header {
            font-size: 1rem;
            color: #4d6e63;
            margin-bottom: 1.2rem;
        }

        .status-pill {
            display: inline-block;
            background: rgba(45, 166, 103, 0.12);
            color: #1f7d4f;
            border: 1px solid rgba(45,166,103,0.18);
            border-radius: 999px;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            font-weight: 700;
            margin-left: 0.5rem;
            vertical-align: middle;
        }

        .section-card {
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(24,84,66,0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 20px rgba(31, 84, 70, 0.05);
        }

        .small-muted {
            color: #5d7169;
            font-size: 0.82rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data loading ----------
BASE_DIR = Path(__file__).resolve().parent

try:
    donation = pd.read_csv(BASE_DIR / "food_selected_for_donation.csv")
except FileNotFoundError:
    donation = pd.DataFrame()

try:
    source_df = pd.read_csv(BASE_DIR / "perishable_goods_management.csv")
except FileNotFoundError:
    source_df = pd.DataFrame()

routing_excel = BASE_DIR / "EcoTrace_Relief_Router_Shortest_Path.xlsx"
if routing_excel.exists():
    try:
        dispatch = pd.read_excel(routing_excel, sheet_name="Shortest Path Dispatch")
        ngo_summary = pd.read_excel(routing_excel, sheet_name="NGO Deliveries Summary")
    except Exception:
        dispatch = donation.copy()
        ngo_summary = pd.DataFrame()
else:
    dispatch = donation.copy()
    ngo_summary = pd.DataFrame()

if donation.empty and not source_df.empty:
    donation = source_df[source_df["was_spoiled"] == 1].copy()
    donation = donation.loc[:, [
        "record_id", "product_id", "product_name", "category", "store_id", "region",
        "expiration_date", "days_until_expiry", "initial_quantity", "units_sold",
        "spoilage_risk", "predicted_spoilage_probability"
    ]].copy()
    donation["available_units"] = (donation["initial_quantity"] - donation["units_sold"]).clip(lower=0).astype(int)
    donation = donation[donation["available_units"] > 0].copy()

# Fallback route fields if Excel export is missing
if "assigned_ngo_id" not in dispatch.columns and not donation.empty:
    dispatch = donation.copy()
    dispatch["assigned_ngo_id"] = "NGO_NE_01"
    dispatch["assigned_ngo_name"] = "City Harvest Food Rescue"
    dispatch["region"] = dispatch["region"].fillna("Northeast")
    dispatch["shortest_distance_km"] = np.random.uniform(15, 220, size=len(dispatch))
    dispatch["est_transit_hours"] = (dispatch["shortest_distance_km"] / 50).round(1)
    dispatch["dispatch_urgency"] = np.where(
        dispatch["days_until_expiry"] == 0,
        "Critical (Immediate)",
        np.where(dispatch["days_until_expiry"] == 1, "High Priority", "Standard Priority"),
    )

if "assigned_ngo_id" in dispatch.columns and ngo_summary.empty:
    ngo_summary = (
        dispatch.groupby(["assigned_ngo_id", "assigned_ngo_name", "region"], as_index=False)
        .agg(
            Total_Batches=("record_id", "count"),
            Total_Units_Received=("available_units", "sum"),
            Avg_Distance_KM=("shortest_distance_km", "mean"),
        )
        .sort_values("Total_Units_Received", ascending=False)
    )
    ngo_summary["Avg_Distance_KM"] = ngo_summary["Avg_Distance_KM"].round(1)

# ---------- Sidebar ----------
st.sidebar.image("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=80", use_container_width=True)
st.sidebar.title("EcoTrace Control")

regions = st.sidebar.multiselect(
    "Regions",
    sorted(dispatch["region"].dropna().unique().tolist()) if "region" in dispatch.columns else ["Northeast", "Southeast", "Midwest", "West", "Southwest"],
    default=sorted(dispatch["region"].dropna().unique().tolist()) if "region" in dispatch.columns else ["Northeast", "Southeast", "Midwest", "West", "Southwest"],
)

categories = st.sidebar.multiselect(
    "Food categories",
    sorted(dispatch["category"].dropna().unique().tolist()) if "category" in dispatch.columns else ["Ready_to_Eat", "Meat", "Seafood", "Bakery"],
    default=sorted(dispatch["category"].dropna().unique().tolist()) if "category" in dispatch.columns else ["Ready_to_Eat", "Meat", "Seafood", "Bakery"],
)

if "days_until_expiry" in dispatch.columns:
    max_days = int(dispatch["days_until_expiry"].max())
    expiry_bounds = st.sidebar.slider("Expiry window (days)", 0, max(3, max_days), (0, max(3, max_days)))
else:
    expiry_bounds = st.sidebar.slider("Expiry window (days)", 0, 3, (0, 3))

if "predicted_spoilage_probability" in dispatch.columns:
    risk_min, risk_max = float(dispatch["predicted_spoilage_probability"].min()), float(dispatch["predicted_spoilage_probability"].max())
    risk_threshold = st.sidebar.slider("Risk threshold", min_value=0.0, max_value=1.0, value=float(risk_min + (risk_max - risk_min) * 0.5), step=0.05)
else:
    risk_threshold = st.sidebar.slider("Risk threshold", min_value=0.0, max_value=1.0, value=0.6, step=0.05)

st.sidebar.caption("Model: Random Forest spoilage prediction")

# ---------- Filtering ----------
filtered = dispatch.copy()
if "region" in filtered.columns:
    filtered = filtered[filtered["region"].isin(regions)] if regions else filtered.iloc[0:0]
if "category" in filtered.columns:
    filtered = filtered[filtered["category"].isin(categories)] if categories else filtered.iloc[0:0]
if "days_until_expiry" in filtered.columns:
    filtered = filtered[
        filtered["days_until_expiry"].between(expiry_bounds[0], expiry_bounds[1])
    ]
if "predicted_spoilage_probability" in filtered.columns:
    filtered = filtered[filtered["predicted_spoilage_probability"] >= risk_threshold]

if filtered.empty:
    filtered = dispatch.copy()

# ---------- Header ----------
header_col = st.columns([5, 2])
with header_col[0]:
    st.markdown('<div class="main-header">EcoTrace Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Food waste reduction and relief routing control center</div>', unsafe_allow_html=True)
with header_col[1]:
    st.markdown('<div class="status-pill">System live</div>', unsafe_allow_html=True)

# ---------- KPI cards ----------
metric_cols = st.columns(4)

if "available_units" in filtered.columns:
    potential_units = int(filtered["available_units"].sum())
else:
    potential_units = int(filtered["initial_quantity"].sum() if "initial_quantity" in filtered.columns else 0)

if "record_id" in filtered.columns:
    batch_count = int(filtered["record_id"].nunique())
else:
    batch_count = int(len(filtered))

if "predicted_spoilage_probability" in filtered.columns:
    avg_risk = round(filtered["predicted_spoilage_probability"].mean(), 3)
else:
    avg_risk = 0.0

if "assigned_ngo_id" in filtered.columns:
    ngo_count = filtered["assigned_ngo_id"].nunique()
else:
    ngo_count = 0

metric_values = [
    ("Batches flagged", f"{batch_count:,}", "📦"),
    ("Units diverted", f"{potential_units:,}", "🥬"),
    ("Avg risk score", f"{avg_risk:.3f}", "⚠️"),
    ("Partner NGOs", f"{ngo_count}", "🤝"),
]

for idx, (label, value, emoji) in enumerate(metric_values):
    with metric_cols[idx]:
        st.markdown(f'<div class="kpi-label">{emoji} {label}</div>', unsafe_allow_html=True)
        st.metric(
            label=label,
            value=value,
            label_visibility="collapsed"
        )

# ---------- Charts ----------
plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    st.markdown('<div class="section-card"><h4 style="margin:0 0 0.75rem 0;">Regional donation volume</h4></div>', unsafe_allow_html=True)
    if "region" in filtered.columns:
        region_summary = filtered.groupby("region")["available_units"].sum().sort_values(ascending=False)
        st.bar_chart(region_summary)
    else:
        st.info("No regional records available for the current filter set.")

with plot_col2:
    st.markdown('<div class="section-card"><h4 style="margin:0 0 0.75rem 0;">Spoilage probability distribution</h4></div>', unsafe_allow_html=True)
    if "predicted_spoilage_probability" in filtered.columns:
        st.area_chart(filtered["predicted_spoilage_probability"].sort_values().reset_index(drop=True))
    else:
        st.info("No prediction data available.")

# ---------- Lower section ----------
left, right = st.columns([1.5, 1])

with left:
    st.markdown('<div class="section-card"><h4 style="margin:0 0 0.75rem 0;">Dispatch manifest</h4></div>', unsafe_allow_html=True)
    display_cols = [
        "record_id",
        "product_name",
        "category",
        "region",
        "store_id",
        "days_until_expiry",
        "available_units",
        "predicted_spoilage_probability",
    ]
    cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[cols].head(20), use_container_width=True)

with right:
    st.markdown('<div class="section-card"><h4 style="margin:0 0 0.75rem 0;">NGO allocations</h4></div>', unsafe_allow_html=True)
    if "assigned_ngo_id" in filtered.columns:
        ngo_table = (
            filtered.groupby(["assigned_ngo_id", "assigned_ngo_name", "region"], as_index=False)
            .agg(
                Total_Batches=("record_id", "count"),
                Units_Received=("available_units", "sum"),
                Avg_Distance_KM=("shortest_distance_km", "mean"),
            )
            .sort_values("Units_Received", ascending=False)
        )
        if "Avg_Distance_KM" in ngo_table.columns:
            ngo_table["Avg_Distance_KM"] = ngo_table["Avg_Distance_KM"].round(1)
        st.dataframe(ngo_table, use_container_width=True)
    else:
        st.info("NGO assignment data will appear here after routing is generated.")

# ---------- Footer insight ----------
if "dispatch_urgency" in filtered.columns:
    urgency_counts = filtered["dispatch_urgency"].value_counts().rename_axis("Priority").reset_index(name="count")
    st.markdown('<div class="section-card"><h4 style="margin:0 0 0.75rem 0;">Urgency overview</h4></div>', unsafe_allow_html=True)
    st.bar_chart(urgency_counts.set_index("Priority")["count"])

st.caption("EcoTrace • Machine learning-driven donation prioritization and humanitarian routing")
