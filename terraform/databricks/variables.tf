variable "workspace_url" {
  description = "Databricks workspace URL (output of the azure stack)."
  type        = string
}

variable "access_connector_id" {
  description = "Resource ID of the Databricks Access Connector (output of the azure stack)."
  type        = string
}

variable "storage_account_name" {
  description = "ADLS Gen2 storage account name (output of the azure stack)."
  type        = string
}

variable "grant_principal" {
  description = "Principal granted read access to the gold schema (group name, user email, or 'account users')."
  type        = string
  default     = "account users"
}
