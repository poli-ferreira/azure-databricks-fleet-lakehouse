output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "storage_account_name" {
  value = azurerm_storage_account.lake.name
}

output "eventhub_namespace" {
  value = azurerm_eventhub_namespace.this.name
}

output "generator_send_connection_string" {
  description = "For the local telemetry generator (send-only)."
  value       = azurerm_eventhub_authorization_rule.generator_send.primary_connection_string
  sensitive   = true
}

output "databricks_listen_connection_string" {
  description = "Goes into a Databricks secret scope (listen-only)."
  value       = azurerm_eventhub_authorization_rule.databricks_listen.primary_connection_string
  sensitive   = true
}

output "databricks_workspace_url" {
  value = var.enable_databricks ? "https://${azurerm_databricks_workspace.this[0].workspace_url}" : null
}

output "access_connector_id" {
  description = "Feed this to the terraform/databricks stack."
  value       = var.enable_databricks ? azurerm_databricks_access_connector.unity[0].id : null
}
