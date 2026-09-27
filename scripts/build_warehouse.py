from __future__ import annotations

from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "data" / "warehouse.duckdb"

RAW_TABLES = [
    "energy_products",
    "technicians",
    "homes",
    "leads",
    "surveys",
    "installations",
    "customer_feedback",
    "regional_weather",
]


def main() -> None:
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(WAREHOUSE)) as connection:
        load_raw_tables(connection)
        run_sql_dir(connection, ROOT / "analytics" / "models")
        run_sql_dir(connection, ROOT / "analytics" / "marts")


def load_raw_tables(connection: duckdb.DuckDBPyConnection) -> None:
    for table in RAW_TABLES:
        csv_path = RAW_DIR / f"{table}.csv"
        connection.execute(f"drop table if exists raw_{table}")
        connection.execute(
            f"""
            create table raw_{table} as
            select * from read_csv_auto(
              '{csv_path.as_posix()}',
              header=true,
              all_varchar=true
            )
            """
        )


def run_sql_dir(connection: duckdb.DuckDBPyConnection, directory: Path) -> None:
    for sql_file in sorted(directory.glob("*.sql")):
        connection.execute(sql_file.read_text())


if __name__ == "__main__":
    main()
