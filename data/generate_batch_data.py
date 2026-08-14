"""Generate batch dimension tables: vehicles.csv and drivers.csv.

Device IDs match the streaming generator (VEH-0000 ... VEH-NNNN) so the
silver-layer join in the pipeline actually resolves.

Usage:
    pip install faker
    python generate_batch_data.py            # writes to ./out/
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from faker import Faker

FLEET_SIZE = 50  # keep in sync with the generator's FLEET_SIZE
OUT_DIR = Path(__file__).parent / "out"

MODELS = [
    ("Volvo", "FH16", "truck"),
    ("Scania", "R450", "truck"),
    ("Mercedes-Benz", "Actros", "truck"),
    ("Ford", "Transit", "van"),
    ("Fiat", "Ducato", "van"),
    ("VW", "Delivery 11.180", "truck"),
]
DEPOTS = ["Sao Paulo Central", "Guarulhos", "Campinas", "Santos Port", "Osasco"]


def main() -> None:
    fake = Faker("pt_BR")
    Faker.seed(42)
    random.seed(42)
    OUT_DIR.mkdir(exist_ok=True)

    drivers = [
        {
            "driver_id": f"DRV-{i:04d}",
            "name": fake.name(),
            "license_category": random.choice(["C", "D", "E"]),
            "hired_date": fake.date_between("-8y", "-30d").isoformat(),
        }
        for i in range(FLEET_SIZE)
    ]

    vehicles = []
    for i in range(FLEET_SIZE):
        make, model, vclass = random.choice(MODELS)
        vehicles.append(
            {
                "device_id": f"VEH-{i:04d}",
                "make": make,
                "model": model,
                "vehicle_class": vclass,
                "year": random.randint(2015, 2025),
                "depot": random.choice(DEPOTS),
                "driver_id": drivers[i]["driver_id"],
                "max_safe_temp": random.choice([105, 110, 115]),
            }
        )

    for name, rows in (("vehicles.csv", vehicles), ("drivers.csv", drivers)):
        path = OUT_DIR / name
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
