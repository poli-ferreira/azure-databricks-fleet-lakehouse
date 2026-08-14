# Standard tier is required for the Kafka protocol endpoint (port 9093),
# which is how the Databricks pipeline consumes the stream.
# 1 TU with auto-inflate off ≈ $0.03/hr — plenty for a 50-device fleet.
resource "azurerm_eventhub_namespace" "this" {
  name                     = "evhns-${var.project}-${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  sku                      = "Standard"
  capacity                 = 1
  auto_inflate_enabled     = false
  tags                     = var.tags
}

resource "azurerm_eventhub" "telemetry" {
  name              = "vehicle-telemetry"
  namespace_id      = azurerm_eventhub_namespace.this.id
  partition_count   = 2
  message_retention = 1
}

# Least-privilege auth rules: the generator can only send,
# the Databricks pipeline can only listen.
resource "azurerm_eventhub_authorization_rule" "generator_send" {
  name                = "generator-send"
  namespace_name      = azurerm_eventhub_namespace.this.name
  eventhub_name       = azurerm_eventhub.telemetry.name
  resource_group_name = azurerm_resource_group.this.name
  send                = true
}

resource "azurerm_eventhub_authorization_rule" "databricks_listen" {
  name                = "databricks-listen"
  namespace_name      = azurerm_eventhub_namespace.this.name
  eventhub_name       = azurerm_eventhub.telemetry.name
  resource_group_name = azurerm_resource_group.this.name
  listen              = true
}
