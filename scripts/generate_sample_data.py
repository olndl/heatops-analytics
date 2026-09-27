from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RANDOM_SEED = 42

REGIONS = ["Berlin", "Brandenburg", "Hamburg", "Saxony", "Bavaria", "NRW"]
PRODUCTS = [
    ("heat_pump", 9500, 2.7),
    ("solar_pv", 7200, 1.8),
    ("wallbox", 1400, 0.4),
]
SOURCES = ["organic", "paid_search", "referral", "partner", "direct"]
HOME_TYPES = ["single_family", "row_house", "multi_family"]
LEAD_STATUSES = ["new", "survey_booked", "quoted", "won", "lost"]
CANCEL_REASONS = ["price", "technical_fit", "timing", "no_response", ""]


def main() -> None:
    random.seed(RANDOM_SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    products = build_products()
    technicians = build_technicians()
    homes = build_homes(420)
    leads = build_leads(homes, 680)
    surveys = build_surveys(leads)
    installations = build_installations(leads, surveys, products, technicians)
    feedback = build_feedback(installations)
    weather = build_weather()

    write_csv("energy_products.csv", products)
    write_csv("technicians.csv", technicians)
    write_csv("homes.csv", homes)
    write_csv("leads.csv", leads)
    write_csv("surveys.csv", surveys)
    write_csv("installations.csv", installations)
    write_csv("customer_feedback.csv", feedback)
    write_csv("regional_weather.csv", weather)


def build_products() -> list[dict[str, object]]:
    return [
        {
            "product_id": f"prod_{index + 1}",
            "product_type": product_type,
            "avg_project_value_eur": value,
            "annual_co2_savings_tons": savings,
        }
        for index, (product_type, value, savings) in enumerate(PRODUCTS)
    ]


def build_technicians() -> list[dict[str, object]]:
    rows = []
    for index in range(24):
        region = REGIONS[index % len(REGIONS)]
        rows.append(
            {
                "technician_id": f"tech_{index + 1:03d}",
                "region": region,
                "team": f"{region[:3].upper()}-{1 + index % 3}",
                "weekly_capacity": random.choice([3, 4, 5, 6]),
                "active": random.random() > 0.08,
            }
        )
    return rows


def build_homes(count: int) -> list[dict[str, object]]:
    rows = []
    for index in range(count):
        rows.append(
            {
                "home_id": f"home_{index + 1:04d}",
                "region": random.choice(REGIONS),
                "home_type": random.choice(HOME_TYPES),
                "build_year": random.randint(1955, 2022),
                "living_area_sqm": random.randint(65, 240),
                "current_heating": random.choice(["gas", "oil", "district", "electric"]),
            }
        )
    return rows


def build_leads(homes: list[dict[str, object]], count: int) -> list[dict[str, object]]:
    rows = []
    start = date(2026, 1, 1)
    for index in range(count):
        created_at = start + timedelta(days=random.randint(0, 180))
        status = random.choices(LEAD_STATUSES, weights=[18, 24, 20, 25, 13])[0]
        rows.append(
            {
                "lead_id": f"lead_{index + 1:05d}",
                "home_id": random.choice(homes)["home_id"],
                "created_at": created_at.isoformat(),
                "source": random.choice(SOURCES),
                "status": status,
                "cancel_reason": random.choice(CANCEL_REASONS) if status == "lost" else "",
            }
        )
    return rows


def build_surveys(leads: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for lead in leads:
        if lead["status"] not in {"survey_booked", "quoted", "won"}:
            continue
        created_at = date.fromisoformat(str(lead["created_at"]))
        survey_at = created_at + timedelta(days=random.randint(2, 18))
        rows.append(
            {
                "survey_id": f"survey_{len(rows) + 1:05d}",
                "lead_id": lead["lead_id"],
                "survey_at": survey_at.isoformat(),
                "technical_fit": random.random() > 0.11,
                "estimated_project_value_eur": random.randint(4500, 18000),
            }
        )
    return rows


def build_installations(
    leads: list[dict[str, object]],
    surveys: list[dict[str, object]],
    products: list[dict[str, object]],
    technicians: list[dict[str, object]],
) -> list[dict[str, object]]:
    survey_by_lead = {row["lead_id"]: row for row in surveys}
    active_technicians = [row for row in technicians if row["active"]]
    rows = []

    for lead in leads:
        if lead["status"] != "won" or lead["lead_id"] not in survey_by_lead:
            continue

        product = random.choice(products)
        technician = random.choice(active_technicians)
        survey_at = date.fromisoformat(str(survey_by_lead[lead["lead_id"]]["survey_at"]))
        scheduled_at = survey_at + timedelta(days=random.randint(8, 55))
        completed = random.random() > 0.22
        completed_at = scheduled_at + timedelta(days=random.randint(0, 8)) if completed else None

        rows.append(
            {
                "installation_id": f"inst_{len(rows) + 1:05d}",
                "lead_id": lead["lead_id"],
                "product_id": product["product_id"],
                "technician_id": technician["technician_id"],
                "scheduled_at": scheduled_at.isoformat(),
                "completed_at": completed_at.isoformat() if completed_at else "",
                "status": "completed" if completed else random.choice(["scheduled", "delayed"]),
                "gross_margin_pct": round(random.uniform(0.18, 0.34), 3),
            }
        )

    return rows


def build_feedback(installations: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for installation in installations:
        if installation["status"] != "completed" or random.random() < 0.18:
            continue
        completed_at = date.fromisoformat(str(installation["completed_at"]))
        rows.append(
            {
                "feedback_id": f"fb_{len(rows) + 1:05d}",
                "installation_id": installation["installation_id"],
                "submitted_at": (completed_at + timedelta(days=random.randint(2, 20))).isoformat(),
                "score": random.choices([1, 2, 3, 4, 5], weights=[2, 4, 10, 36, 48])[0],
                "comment_category": random.choice(
                    ["communication", "speed", "quality", "price", "cleanliness"]
                ),
            }
        )
    return rows


def build_weather() -> list[dict[str, object]]:
    rows = []
    for region in REGIONS:
        for month in range(1, 7):
            rows.append(
                {
                    "region": region,
                    "month": f"2026-{month:02d}",
                    "avg_temperature_c": round(random.uniform(-1.5, 22.0), 1),
                    "heating_degree_days": random.randint(20, 520),
                }
            )
    return rows


def write_csv(filename: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path = RAW_DIR / filename
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
