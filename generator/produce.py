"""Synthetic vehicle telemetry producer for Azure Event Hubs.

Simulates a fixed fleet of devices emitting JSON telemetry. A configurable
fraction of events is deliberately malformed (nulls, out-of-range values,
bad timestamps) so the downstream pipeline's data-quality expectations have
something real to catch.

Environment variables:
    EVENTHUB_CONNECTION_STR  send-only connection string (required)
    EVENTHUB_NAME            event hub name            (default: vehicle-telemetry)
    FLEET_SIZE               number of devices          (default: 50)
    EVENTS_PER_BATCH         events per send            (default: 25)
    BATCH_INTERVAL_SECONDS   pause between batches      (default: 1.0)
    DIRTY_RATIO              fraction of bad events     (default: 0.05)

Usage:
    export EVENTHUB_CONNECTION_STR="Endpoint=sb://..."
    python produce.py
"""

from __future__ import annotations

import json
import os
import random
import signal
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from azure.eventhub import EventData, EventHubProducerClient

FLEET_SIZE = int(os.environ.get("FLEET_SIZE", "50"))
EVENTS_PER_BATCH = int(os.environ.get("EVENTS_PER_BATCH", "25"))
BATCH_INTERVAL_SECONDS = float(os.environ.get("BATCH_INTERVAL_SECONDS", "1.0"))
DIRTY_RATIO = float(os.environ.get("DIRTY_RATIO", "0.05"))

# Rough bounding box around São Paulo so the gold-layer map looks plausible.
LAT_RANGE = (-23.75, -23.35)
LON_RANGE = (-46.85, -46.35)


@dataclass
class Vehicle:
    """Random-walk state so consecutive readings per device are correlated."""

    device_id: str
    lat: float
    lon: float
    speed: float
    engine_temp: float
    fuel_pct: float

    def tick(self) -> dict:
        self.speed = max(0.0, min(160.0, self.speed + random.uniform(-8, 8)))
        self.engine_temp = max(60.0, min(130.0, self.engine_temp + random.uniform(-1.5, 2.0)))
        self.fuel_pct = max(0.0, self.fuel_pct - random.uniform(0.0, 0.05))
        if self.fuel_pct < 2.0:  # refuel
            self.fuel_pct = 100.0
        self.lat += random.uniform(-0.002, 0.002)
        self.lon += random.uniform(-0.002, 0.002)
        return {
            "device_id": self.device_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "speed": round(self.speed, 1),
            "engine_temp": round(self.engine_temp, 1),
            "fuel_pct": round(self.fuel_pct, 2),
            "latitude": round(self.lat, 6),
            "longitude": round(self.lon, 6),
        }


def make_fleet(size: int) -> list[Vehicle]:
    return [
        Vehicle(
            device_id=f"VEH-{i:04d}",
            lat=random.uniform(*LAT_RANGE),
            lon=random.uniform(*LON_RANGE),
            speed=random.uniform(0, 100),
            engine_temp=random.uniform(80, 100),
            fuel_pct=random.uniform(20, 100),
        )
        for i in range(size)
    ]


def corrupt(event: dict) -> dict:
    """Inject one of several realistic data-quality failures."""
    bad = dict(event)
    match random.choice(["null_device", "negative_speed", "sensor_max", "bad_ts", "null_temp"]):
        case "null_device":
            bad["device_id"] = None
        case "negative_speed":
            bad["speed"] = -abs(bad["speed"]) - 1
        case "sensor_max":
            bad["engine_temp"] = 999.0
        case "bad_ts":
            bad["ts"] = "not-a-timestamp"
        case "null_temp":
            bad["engine_temp"] = None
    return bad


def main() -> None:
    conn_str = os.environ.get("EVENTHUB_CONNECTION_STR")
    if not conn_str:
        sys.exit("EVENTHUB_CONNECTION_STR is not set (use the send-only connection string).")
    hub_name = os.environ.get("EVENTHUB_NAME", "vehicle-telemetry")

    producer = EventHubProducerClient.from_connection_string(conn_str, eventhub_name=hub_name)
    fleet = make_fleet(FLEET_SIZE)
    running = True

    def stop(*_: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    sent = dirty = 0
    print(f"Streaming {FLEET_SIZE} devices -> {hub_name} (Ctrl+C to stop)")
    with producer:
        while running:
            batch = producer.create_batch()
            for vehicle in random.sample(fleet, min(EVENTS_PER_BATCH, len(fleet))):
                event = vehicle.tick()
                if random.random() < DIRTY_RATIO:
                    event = corrupt(event)
                    dirty += 1
                # Partition by device so per-device ordering is preserved.
                batch.add(EventData(json.dumps(event)))
                sent += 1
            producer.send_batch(batch)
            if sent % 500 < EVENTS_PER_BATCH:
                print(f"  sent={sent} dirty={dirty} ({dirty / max(sent, 1):.1%})")
            time.sleep(BATCH_INTERVAL_SECONDS)

    print(f"Stopped. Total sent={sent}, dirty={dirty}.")


if __name__ == "__main__":
    main()
