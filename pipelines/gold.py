"""Gold layer: business-level aggregates for dashboards and alerting."""

import dlt
from pyspark.sql.functions import avg, col, count, max as max_, round as round_, window


@dlt.table(
    name="gold.device_health",
    comment="Per-device health metrics in 10-minute windows.",
    table_properties={"quality": "gold"},
)
def device_health():
    t = dlt.read_stream("silver.telemetry").withWatermark("ts", "15 minutes")
    return (
        t.groupBy(window(col("ts"), "10 minutes"), col("device_id"))
        .agg(
            round_(avg("engine_temp"), 1).alias("avg_engine_temp"),
            round_(max_("engine_temp"), 1).alias("max_engine_temp"),
            round_(avg("speed"), 1).alias("avg_speed"),
            round_(max_("speed"), 1).alias("max_speed"),
            count("*").alias("reading_count"),
        )
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            "device_id",
            "avg_engine_temp",
            "max_engine_temp",
            "avg_speed",
            "max_speed",
            "reading_count",
        )
    )


@dlt.table(
    name="gold.overheat_alerts",
    comment="Readings above each vehicle's max safe temperature, enriched with vehicle and driver.",
    table_properties={"quality": "gold"},
)
def overheat_alerts():
    telemetry = dlt.read_stream("silver.telemetry")
    vehicles = dlt.read("silver.vehicles")
    drivers = dlt.read("silver.drivers")
    return (
        telemetry.join(vehicles, "device_id")
        .where(col("engine_temp") > col("max_safe_temp"))
        .join(drivers, "driver_id", "left")
        .select(
            "ts",
            "device_id",
            "engine_temp",
            "max_safe_temp",
            "speed",
            "latitude",
            "longitude",
            "make",
            "model",
            "depot",
            "driver_id",
            col("name").alias("driver_name"),
        )
    )


@dlt.table(
    name="gold.fleet_daily_summary",
    comment="Daily fleet-level KPIs per depot (batch recompute each pipeline run).",
    table_properties={"quality": "gold"},
)
def fleet_daily_summary():
    telemetry = dlt.read("silver.telemetry")
    vehicles = dlt.read("silver.vehicles")
    return (
        telemetry.join(vehicles, "device_id")
        .groupBy(col("ts").cast("date").alias("date"), "depot")
        .agg(
            count("*").alias("readings"),
            round_(avg("speed"), 1).alias("avg_speed"),
            round_(avg("engine_temp"), 1).alias("avg_engine_temp"),
            round_(avg("fuel_pct"), 1).alias("avg_fuel_pct"),
        )
    )
