# Workspace-level Unity Catalog objects. Prerequisite: the workspace is
# attached to a metastore (automatic in most regions for new accounts;
# otherwise create/attach one in the account console first).

resource "databricks_storage_credential" "lake" {
  name = "fleet-lake-credential"

  azure_managed_identity {
    access_connector_id = var.access_connector_id
  }

  comment = "Managed identity via Access Connector - no storage keys."
}

resource "databricks_external_location" "lakehouse" {
  name            = "fleet-lakehouse"
  url             = "abfss://lakehouse@${var.storage_account_name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.lake.name
  comment         = "Root for the fleet catalog's managed tables."
}

resource "databricks_external_location" "landing" {
  name            = "fleet-landing"
  url             = "abfss://landing@${var.storage_account_name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.lake.name
  comment         = "Batch CSV drop zone read by Auto Loader."
}

resource "databricks_catalog" "fleet" {
  name         = "fleet"
  storage_root = databricks_external_location.lakehouse.url
  comment      = "Fleet telemetry lakehouse - medallion architecture."

  depends_on = [databricks_external_location.lakehouse]
}

resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.fleet.name
  name         = "bronze"
  comment      = "Raw ingested data, append-only."
}

resource "databricks_schema" "silver" {
  catalog_name = databricks_catalog.fleet.name
  name         = "silver"
  comment      = "Typed, validated, deduplicated."
}

resource "databricks_schema" "gold" {
  catalog_name = databricks_catalog.fleet.name
  name         = "gold"
  comment      = "Business-level aggregates for consumption."
}
