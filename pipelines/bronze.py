"""Bronze layer: raw streaming ingest from Azure Event Hubs.

Event Hubs Standard tier exposes a Kafka-compatible endpoint on port 9093,
so we consume it with Spark's built-in Kafka source — no extra libraries.
Auth uses the listen-only connection string from the 'fleet' secret scope
(created by scripts/setup_secrets.sh).
"""

import dlt
from pyspark.sql.functions import col, current_timestamp

SCOPE = "fleet"
EVENTHUB_NAME = "vehicle-telemetry"

namespace = dbutils.secrets.get(SCOPE, "eventhubs-namespace")  # noqa: F821
connection = dbutils.secrets.get(SCOPE, "eventhubs-listen-connection")  # noqa: F821

KAFKA_OPTIONS = {
    "kafka.bootstrap.servers": f"{namespace}.servicebus.windows.net:9093",
    "subscribe": EVENTHUB_NAME,
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.mechanism": "PLAIN",
    "kafka.sasl.jaas.config": (
        "kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required "
        f'username="$ConnectionString" password="{connection}";'
    ),
    "kafka.request.timeout.ms": "60000",
    "kafka.session.timeout.ms": "30000",
    "startingOffsets": "earliest",
    "failOnDataLoss": "false",
}


@dlt.table(
    name="bronze.telemetry_raw",
    comment="Raw telemetry events from Event Hubs. Append-only, value kept as string.",
    table_properties={"quality": "bronze"},
)
def telemetry_raw():
    return (
        spark.readStream.format("kafka")  # noqa: F821
        .options(**KAFKA_OPTIONS)
        .load()
        .select(
            col("value").cast("string").alias("raw_payload"),
            col("timestamp").alias("event_hub_ts"),
            col("partition"),
            col("offset"),
            current_timestamp().alias("ingested_at"),
        )
    )
