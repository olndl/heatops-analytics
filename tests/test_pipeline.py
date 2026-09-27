from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = ROOT / "data" / "warehouse.duckdb"


def test_pipeline_builds_business_marts() -> None:
    subprocess.run([sys.executable, "scripts/generate_sample_data.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/build_warehouse.py"], cwd=ROOT, check=True)

    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "select table_name from information_schema.tables"
            ).fetchall()
        }
        assert "mart_installation_funnel" in tables
        assert "mart_installation_operations" in tables
        assert "mart_customer_experience" in tables


def test_quality_checks_pass_on_generated_data() -> None:
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        for check_file in sorted((ROOT / "analytics" / "quality_checks").glob("*.sql")):
            failures = connection.execute(check_file.read_text()).fetchall()
            assert failures == [], check_file.name


def test_core_kpis_are_available() -> None:
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        row = connection.execute(
            """
            select
              sum(leads) as leads,
              sum(completed_installations) as completed_installations,
              avg(lead_to_survey_rate) as avg_lead_to_survey_rate
            from mart_installation_funnel
            """
        ).fetchone()

    assert row[0] > 0
    assert row[1] > 0
    assert 0 <= row[2] <= 1
