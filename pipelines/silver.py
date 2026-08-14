"""Silver layer: typed telemetry with data-quality gates, plus batch dims.

Patterns demonstrated:
  - expectations (expect_or_drop) as declarative quality gates
  - an explicit quarantine table capturing what was rejected and why
  - watermark + dropDuplicates for late/duplicate streaming data
  - Auto Loader (cloudFiles) for the batch dimension CSVs
"""

import dlt
from pyspark.sql.functions import col, from_json, when
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

LANDING = "abfss://landing@{storage_account}.dfs.core.windows.net"
# Set storage_account in the pipeline configuration (key: storage_account),
# read here via spark.conf.
TELEMETRY_SCHEMA = StructType(
    [
        StructField("device_id", StringType()),
        StructField("ts", StringType()),
        StructField("speed", DoubleType()),
        StructField("engine_temp", DoubleType()),
        StructField("fuel_pct", DoubleType()),
        StructField("latitude", DoubleType()),
        StructField("longitude", DoubleType()),
    ]
)

VALID = (
    "device_id IS NOT NULL AND ts IS NOT NULL "
    "AND speed BETWEEN 0 AND 220 "
    "AND engine_temp BETWEEN 40 AND 200"
)


def _parsed():
    return (
        dlt.read_stream("bronze.telemetry_raw")
        .select(from_json(col("raw_payload"), TELEMETRY_SCHEMA).alias("j"), col("ingested_at"))
        .select("j.*", "ingested_at")
        .withColumn("ts", col("ts").cast("timestamp"))
    )


@dlt.table(
    name="silver.telemetry",
    comment="Typed, validated, deduplicated telemetry.",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_record", VALID)
@dlt.expect("plausible_location", "latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180")
def telemetry():
    return (
        _parsed()
        .withWatermark("ts", "10 minutes")
        .dropDuplicates(["device_id", "ts"])
    )


@dlt.table(
    name="silver.telemetry_quarantine",
    comment="Records rejected by silver.telemetry's quality gates, tagged with a reason.",
    table_properties={"quality": "silver"},
)
def telemetry_quarantine():
    df = _parsed()
    return df.where(f"NOT ({VALID}) OR ts IS NULL").withColumn(
        "reject_reason",
        when(col("device_id").isNull(), "null_device_id")
        .when(col("ts").isNull(), "bad_timestamp")
        .when((col("speed") < 0) | (col("speed") > 220), "speed_out_of_range")
        .otherwise("temp_out_of_range"),
    )


@dlt.table(
    name="silver.vehicles",
    comment="Vehicle dimension loaded from the landing container via Auto Loader.",
)
@dlt.expect_or_drop("has_device_id", "device_id IS NOT NULL")
def vehicles():
    storage_account = spark.conf.get("storage_account")  # noqa: F821
    return (
        spark.readStream.format("cloudFiles")  # noqa: F821
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("header", "true")
        .load(f"{LANDING.format(storage_account=storage_account)}/vehicles/")
    )


@dlt.table(
    name="silver.drivers",
    comment="Driver dimension loaded from the landing container via Auto Loader.",
)
@dlt.expect_or_drop("has_driver_id", "driver_id IS NOT NULL")
def drivers():
    storage_account = spark.conf.get("storage_account")  # noqa: F821
    return (
        spark.readStream.format("cloudFiles")  # noqa: F821
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("header", "true")
        .load(f"{LANDING.format(storage_account=storage_account)}/drivers/")
    )
