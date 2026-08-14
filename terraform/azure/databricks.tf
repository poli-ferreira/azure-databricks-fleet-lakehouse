# Everything in this file is gated behind enable_databricks so the
# 14-day trial clock doesn't start until you're ready (see variables.tf).

# Premium SKU is required for Unity Catalog. The trial discount applies
# automatically to a new workspace in a trial-eligible subscription.
resource "azurerm_databricks_workspace" "this" {
  count = var.enable_databricks ? 1 : 0

  name                        = "dbw-${var.project}-lakehouse"
  resource_group_name         = azurerm_resource_group.this.name
  location                    = azurerm_resource_group.this.location
  sku                         = "premium"
  managed_resource_group_name = "rg-${var.project}-lakehouse-managed"
  tags                        = var.tags
}

# The Access Connector is the bridge that lets Unity Catalog reach ADLS
# with a managed identity — no storage keys or secrets anywhere in code.
resource "azurerm_databricks_access_connector" "unity" {
  count = var.enable_databricks ? 1 : 0

  name                = "dbac-${var.project}-unity"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "unity_storage" {
  count = var.enable_databricks ? 1 : 0

  scope                = azurerm_storage_account.lake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.unity[0].identity[0].principal_id
}
