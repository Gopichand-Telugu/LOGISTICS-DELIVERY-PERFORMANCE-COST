"""Plotly chart helpers shared by the dashboard and notebook."""

import pandas as pd
import plotly.express as px


PALETTE = ["#087E6E", "#F26A4B", "#E6B84C", "#375B8A", "#6A9B7A", "#9B5D45"]


def monthly_performance_chart(data: pd.DataFrame):
    monthly = data.groupby("order_month", as_index=False).agg(
        orders=("order_id", "nunique"), on_time_rate=("on_time", "mean")
    )
    figure = px.line(
        monthly,
        x="order_month",
        y="on_time_rate",
        markers=True,
        title="Monthly on-time rate",
        color_discrete_sequence=[PALETTE[0]],
    )
    figure.update_yaxes(tickformat=".0%", title="On-time rate")
    figure.update_xaxes(title="Order month")
    figure.update_layout(margin=dict(l=12, r=12, t=48, b=12), height=320)
    return figure


def partner_performance_chart(data: pd.DataFrame):
    partner = data.groupby("delivery_partner", as_index=False).agg(
        orders=("order_id", "nunique"), on_time_rate=("on_time", "mean"), avg_shipping_cost=("shipping_cost", "mean")
    )
    partner = partner.sort_values("on_time_rate", ascending=True)
    figure = px.bar(
        partner,
        x="on_time_rate",
        y="delivery_partner",
        orientation="h",
        color="avg_shipping_cost",
        color_continuous_scale=["#E6B84C", "#087E6E"],
        hover_data={"orders": True, "avg_shipping_cost": ":.2f", "on_time_rate": ":.1%"},
        title="Partner on-time rate and average shipping cost",
    )
    figure.update_xaxes(tickformat=".0%", title="On-time rate")
    figure.update_yaxes(title="")
    figure.update_layout(margin=dict(l=12, r=12, t=48, b=12), height=360, coloraxis_colorbar_title="Avg cost")
    return figure


def mode_cost_chart(data: pd.DataFrame):
    mode = data.groupby("shipping_mode", as_index=False).agg(
        avg_shipping_cost=("shipping_cost", "mean"), avg_tracked_total_cost=("tracked_total_cost", "mean")
    )
    long_mode = mode.melt(id_vars="shipping_mode", var_name="cost_type", value_name="average_cost")
    figure = px.bar(
        long_mode,
        x="shipping_mode",
        y="average_cost",
        color="cost_type",
        barmode="group",
        color_discrete_sequence=PALETTE[:2],
        title="Average cost by mode",
    )
    figure.update_xaxes(title="Shipping mode")
    figure.update_yaxes(title="Average cost")
    figure.update_layout(margin=dict(l=12, r=12, t=48, b=12), height=320, legend_title="")
    return figure