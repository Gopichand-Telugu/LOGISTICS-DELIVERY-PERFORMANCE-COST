"""Interactive logistics delivery performance and cost dashboard."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.business_analysis import add_business_metrics, summarize_business
from src.data_cleaner import clean_data
from src.data_loader import load_data
from src.visualization import mode_cost_chart, monthly_performance_chart, partner_performance_chart


st.set_page_config(page_title="Logistics | Delivery & Cost", page_icon="📦", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: 0; }
    [data-testid="stHeading"] h1 { font-size: 2rem; line-height: 1.2; }
    .stApp { background: #f4f5f1; }
    [data-testid="stSidebar"] { background: #e9eee8; }
    [data-testid="stMetric"] { background: #ffffff; border: 1px solid #dfe5de; border-left: 4px solid #087e6e; padding: 14px 16px; border-radius: 5px; }
    [data-testid="stMetricLabel"] { color: #53615b; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading orders...")
def get_orders() -> pd.DataFrame:
    return add_business_metrics(clean_data(load_data()))


orders = get_orders()
st.title("Delivery performance & cost")
st.caption("Order-level view of delivery reliability, shipping spend, and partner performance")

with st.sidebar:
    st.header("Filters")
    date_min = orders["order_date"].min().date()
    date_max = orders["order_date"].max().date()
    date_range = st.date_input("Order date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    modes = st.multiselect("Shipping mode", sorted(orders["shipping_mode"].dropna().unique()), default=sorted(orders["shipping_mode"].dropna().unique()))
    partners = st.multiselect("Delivery partner", sorted(orders["delivery_partner"].dropna().unique()), default=sorted(orders["delivery_partner"].dropna().unique()))
    timeliness = st.radio("Timeliness", ["All orders", "On time", "Late"], horizontal=False)

filtered = orders.copy()
if len(date_range) == 2:
    filtered = filtered[filtered["order_date"].dt.date.between(date_range[0], date_range[1])]
filtered = filtered[filtered["shipping_mode"].isin(modes) & filtered["delivery_partner"].isin(partners)]
if timeliness == "On time":
    filtered = filtered[filtered["on_time"]]
elif timeliness == "Late":
    filtered = filtered[~filtered["on_time"]]

if filtered.empty:
    st.warning("No orders match these filters. Widen the date range or select more modes and partners.")
    st.stop()

metrics = summarize_business(filtered)
first_row = st.columns(2)
first_row[0].metric("Total orders", f"{metrics['orders']:,}")
first_row[1].metric("On-time delivery", f"{metrics['on_time_rate_pct']:.1f}%")

second_row = st.columns(2)
second_row[0].metric("Avg. shipping cost", f"{metrics['average_shipping_cost']:,.0f}")
second_row[1].metric("Avg. rating", f"{metrics['average_customer_rating']:.2f} / 5")

third_row = st.columns(2)
third_row[0].metric("Avg. shipping + fuel", f"{metrics['average_tracked_total_cost']:,.0f}")
third_row[1].metric("Avg. late delay", f"{metrics['average_delay_days_late_only']:.1f} days")

fourth_row = st.columns(2)
fourth_row[0].metric("Damaged orders", f"{metrics['damaged_order_rate_pct']:.1f}%")
fourth_row[1].metric("Returned orders", f"{metrics['returned_order_rate_pct']:.1f}%")

left, right = st.columns([1.1, 1])
with left:
    st.plotly_chart(monthly_performance_chart(filtered), width="stretch")
with right:
    st.plotly_chart(mode_cost_chart(filtered), width="stretch")

st.plotly_chart(partner_performance_chart(filtered), width="stretch")

st.subheader("Shipment cost and distance")
scatter = px.scatter(
    filtered,
    x="distance_km",
    y="shipping_cost",
    color="shipping_mode",
    hover_data=["order_id", "delivery_partner", "destination_city", "on_time", "delay_days"],
    color_discrete_sequence=["#087E6E", "#F26A4B", "#375B8A", "#E6B84C"],
    labels={"distance_km": "Distance (km)", "shipping_cost": "Shipping cost"},
)
scatter.update_layout(margin=dict(l=12, r=12, t=12, b=12), height=380, legend_title="Mode")
st.plotly_chart(scatter, width="stretch")

st.subheader("Orders")
table_columns = [
    "order_id", "order_date", "origin_city", "destination_city", "distance_km",
    "shipping_mode", "delivery_partner", "shipping_cost", "fuel_cost", "delivery_status",
    "on_time", "delay_days", "customer_rating",
]
st.dataframe(filtered[table_columns].sort_values("order_date", ascending=False), width="stretch", hide_index=True)