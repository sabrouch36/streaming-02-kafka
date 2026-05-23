"""Kafka Streaming Sales Dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

# =========================================================
# DATA SOURCE
# =========================================================

CSV_PATH = Path("data/output/consumed_sales.csv")


def load_data():
    """Load streaming sales data."""
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)

    return pd.DataFrame()


# =========================================================
# UI
# =========================================================

app_ui = ui.page_fluid(
    ui.h1(
        "Kafka Streaming Sales Dashboard",
        style="""
        color:#38bdf8;
        font-size:42px;
        font-weight:700;
        margin-bottom:30px;
        """,
    ),
    ui.p(
        "Real-Time Kafka Streaming Analytics",
        style="""
        color:#cbd5e1;
        font-size:18px;
        margin-bottom:35px;
        """,
    ),
    # =====================================================
    # KPI CARDS
    # =====================================================
    ui.layout_columns(
        ui.value_box(
            "Messages Processed",
            ui.output_text("messages_count"),
            theme="bg-gradient-blue-purple",
        ),
        ui.value_box(
            "Total Sales",
            ui.output_text("total_sales"),
            theme="bg-gradient-green-teal",
        ),
        ui.value_box(
            "Average Sale",
            ui.output_text("average_sale"),
            theme="bg-gradient-orange-red",
        ),
        ui.value_box(
            "Unique Customers",
            ui.output_text("unique_customers"),
            theme="bg-gradient-indigo-purple",
        ),
    ),
    ui.hr(),
    # =====================================================
    # CHARTS
    # =====================================================
    ui.layout_columns(
        ui.card(
            ui.card_header("Sales by Device Type"),
            output_widget("device_chart"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Payment Method Distribution"),
            output_widget("payment_chart"),
            full_screen=True,
        ),
    ),
    ui.hr(),
    ui.layout_columns(
        ui.card(
            ui.card_header("Customer Activity"),
            output_widget("customer_chart"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Referral Sources"),
            output_widget("referral_chart"),
            full_screen=True,
        ),
    ),
    ui.hr(),
    # =====================================================
    # TABLE
    # =====================================================
    ui.h3("Latest Streamed Sales", style="margin-top:20px;"),
    ui.output_data_frame("sales_table"),
    style="""
    background-color: #0f172a;
    color: white;
    padding: 25px;
    font-family: Arial;
    """,
)


# =========================================================
# SERVER
# =========================================================


def server(input, output, session):
    """Run dashboard server logic."""

    @reactive.calc
    def sales_data():
        reactive.invalidate_later(3000)
        return load_data()

    # =====================================================
    # KPIs
    # =====================================================

    @render.text
    def messages_count():
        df = sales_data()
        return f"{len(df)}"

    @render.text
    def total_sales():
        df = sales_data()

        if len(df) == 0:
            return "$0"

        total = len(df) * 49.99
        return f"${total:.2f}"

    @render.text
    def average_sale():
        df = sales_data()

        if len(df) == 0:
            return "$0"

        return "$49.99"

    @render.text
    def unique_customers():
        df = sales_data()

        if len(df) == 0:
            return "0"

        if "customer_id" not in df.columns:
            return "0"

        return str(df["customer_id"].nunique())

    # =====================================================
    # DEVICE CHART
    # =====================================================

    @render_widget
    def device_chart():

        df = sales_data()

        if len(df) == 0:
            return None

        chart_data = df["device_type"].value_counts().reset_index()

        chart_data.columns = ["device_type", "count"]

        fig = px.bar(
            chart_data,
            x="device_type",
            y="count",
            color="device_type",
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font_color="white",
            height=450,
        )

        return fig

    # =====================================================
    # PAYMENT CHART
    # =====================================================

    @render_widget
    def payment_chart():

        df = sales_data()

        if len(df) == 0:
            return None

        chart_data = df["payment_method"].value_counts().reset_index()

        chart_data.columns = ["payment_method", "count"]

        fig = px.pie(
            chart_data,
            names="payment_method",
            values="count",
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="#111827",
            font_color="white",
            height=450,
        )

        return fig

    # =====================================================
    # CUSTOMER CHART
    # =====================================================

    @render_widget
    def customer_chart():

        df = sales_data()

        if len(df) == 0:
            return None

        customer_counts = df["customer_id"].value_counts().head(10).reset_index()

        customer_counts.columns = ["customer_id", "count"]

        fig = px.bar(
            customer_counts,
            x="customer_id",
            y="count",
            color="count",
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font_color="white",
            height=450,
        )

        return fig

    # =====================================================
    # REFERRAL CHART
    # =====================================================

    @render_widget
    def referral_chart():

        df = sales_data()

        if len(df) == 0:
            return None

        referral_data = df["referral_source"].value_counts().reset_index()

        referral_data.columns = ["referral_source", "count"]

        fig = px.bar(
            referral_data,
            x="referral_source",
            y="count",
            color="referral_source",
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font_color="white",
            height=450,
        )

        return fig

    # =====================================================
    # TABLE
    # =====================================================

    @render.data_frame
    def sales_table():

        df = sales_data()

        if len(df) == 0:
            return pd.DataFrame()

        return render.DataGrid(
            df.tail(15),
            width="100%",
        )


# =========================================================
# APP
# =========================================================

app = App(app_ui, server)
