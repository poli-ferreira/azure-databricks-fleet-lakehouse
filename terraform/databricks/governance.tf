# Example Unity Catalog governance: read-only access to the gold layer
# without touching bronze/silver. "account users" is the built-in group
# covering everyone in the Databricks account - swap grant_principal for
# a real group (e.g. "analysts") once one exists.

resource "databricks_grants" "gold_readonly" {
  schema = databricks_schema.gold.id

  grant {
    principal  = var.grant_principal
    privileges = ["SELECT", "USE_SCHEMA"]
  }
}
