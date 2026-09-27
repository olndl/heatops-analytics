from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = ROOT / "data" / "warehouse.duckdb"


st.set_page_config(page_title="HeatOps Analytics", layout="wide")


@st.cache_data
def query(sql: str) -> pd.DataFrame:
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        return connection.execute(sql).df()


def main() -> None:
    st.title("HeatOps Analytics")
    st.caption("Residential energy installation KPIs and data quality monitor")

    if not WAREHOUSE.exists():
        st.error("Warehouse not found. Run scripts/generate_sample_data.py and scripts/build_warehouse.py first.")
        return

    funnel = query("select * from mart_installation_funnel")
    operations = query("select * from mart_installation_operations")
    feedback = query("select * from mart_customer_experience")

    regions = sorted(value for value in funnel["region"].dropna().unique())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
    filtered_funnel = funnel[funnel["region"].isin(selected_regions)]
    filtered_operations = operations[operations["region"].isin(selected_regions)]
    filtered_feedback = feedback[feedback["region"].isin(selected_regions)]

    render_kpis(filtered_funnel, filtered_operations, filtered_feedback)
    render_funnel(filtered_funnel)
    render_operations(filtered_operations)
    render_quality_checks()


def render_kpis(
    funnel: pd.DataFrame,
    operations: pd.DataFrame,
    feedback: pd.DataFrame,
) -> None:
    completed = int(funnel["completed_installations"].sum())
    leads = int(funnel["leads"].sum())
    conversion = completed / leads if leads else 0
    backlog = int(operations["open_backlog"].sum())
    savings = float(operations["annual_co2_savings_tons"].sum())
    avg_score = feedback["avg_score"].dropna().mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Leads", f"{leads:,}")
    col2.metric("Completed installs", f"{completed:,}")
    col3.metric("Lead to install", f"{conversion:.1%}")
    col4.metric("Open backlog", f"{backlog:,}")
    col5.metric("CO2 reduction / year", f"{savings:,.1f} t")
    st.caption(f"Average customer score: {avg_score:.2f} / 5")


def render_funnel(funnel: pd.DataFrame) -> None:
    st.subheader("Funnel performance")
    by_region = (
        funnel.groupby("region", as_index=False)
        .agg(
            leads=("leads", "sum"),
            surveys=("surveys", "sum"),
            completed_installations=("completed_installations", "sum"),
        )
        .sort_values("completed_installations", ascending=False)
    )
    st.plotly_chart(
        px.bar(
            by_region,
            x="region",
            y=["leads", "surveys", "completed_installations"],
            barmode="group",
            labels={"value": "Count", "variable": "Stage"},
        ),
        use_container_width=True,
    )


def render_operations(operations: pd.DataFrame) -> None:
    st.subheader("Operations and backlog")
    by_product = (
        operations.groupby("product_type", as_index=False)
        .agg(
            open_backlog=("open_backlog", "sum"),
            median_days_from_survey=("median_days_from_survey", "median"),
            annual_co2_savings_tons=("annual_co2_savings_tons", "sum"),
        )
        .sort_values("open_backlog", ascending=False)
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            px.bar(
                by_product,
                x="product_type",
                y="open_backlog",
                labels={"product_type": "Product", "open_backlog": "Open backlog"},
            ),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            px.scatter(
                by_product,
                x="median_days_from_survey",
                y="annual_co2_savings_tons",
                size="open_backlog",
                color="product_type",
                labels={
                    "median_days_from_survey": "Median days from survey",
                    "annual_co2_savings_tons": "CO2 reduction / year",
                },
            ),
            use_container_width=True,
        )

    st.dataframe(operations.sort_values(["region", "product_type"]), use_container_width=True)


def render_quality_checks() -> None:
    st.subheader("Data quality checks")
    check_dir = ROOT / "analytics" / "quality_checks"
    rows = []
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        for check_file in sorted(check_dir.glob("*.sql")):
            failures = connection.execute(check_file.read_text()).df()
            rows.append(
                {
                    "check": check_file.stem,
                    "failing_rows": len(failures),
                    "status": "pass" if failures.empty else "review",
                }
            )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
