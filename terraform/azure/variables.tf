variable "project" {
  description = "Short project slug used in resource names."
  type        = string
  default     = "fleet"
}

variable "location" {
  description = "Azure region for all resources. Pick one and stay in it."
  type        = string
  default     = "eastus"
}

variable "enable_databricks" {
  description = <<-EOT
    Creates the Databricks workspace and Unity Catalog access connector.
    Leave false until the Azure infra + generator are working: the 14-day
    Databricks trial clock starts when the workspace is created.
  EOT
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags applied to every resource."
  type        = map(string)
  default = {
    project    = "fleet-lakehouse"
    managed_by = "terraform"
    purpose    = "portfolio"
  }
}
