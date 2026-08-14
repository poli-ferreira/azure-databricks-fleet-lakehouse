resource "azurerm_resource_group" "this" {
  name     = "rg-${var.project}-lakehouse"
  location = var.location
  tags     = var.tags
}

# Storage account names must be globally unique, lowercase, <= 24 chars.
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}
