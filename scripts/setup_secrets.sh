#!/usr/bin/env bash
# Create the Databricks secret scope holding the Event Hubs listen
# connection string, read by the pipeline at runtime.
# Prereq: databricks auth login --host <workspace-url>
set -euo pipefail

SCOPE="fleet"
CONN=$(cd terraform/azure && terraform output -raw databricks_listen_connection_string)
NAMESPACE=$(cd terraform/azure && terraform output -raw eventhub_namespace)

databricks secrets create-scope "$SCOPE" 2>/dev/null || echo "scope '$SCOPE' already exists"
databricks secrets put-secret "$SCOPE" eventhubs-listen-connection --string-value "$CONN"
databricks secrets put-secret "$SCOPE" eventhubs-namespace --string-value "$NAMESPACE"

echo "Secrets stored in scope '$SCOPE': eventhubs-listen-connection, eventhubs-namespace"
