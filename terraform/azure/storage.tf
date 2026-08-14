# ADLS Gen2: hierarchical namespace ON is what makes this a data lake
# rather than plain blob storage.
resource "azurerm_storage_account" "lake" {
  name                     = "st${var.project}lake${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
  tags                     = var.tags
}

# lakehouse: Unity Catalog managed storage (catalog storage root / external location)
# landing:   batch CSV drop zone read by Auto Loader
resource "azurerm_storage_data_lake_gen2_filesystem" "lakehouse" {
  name               = "lakehouse"
  storage_account_id = azurerm_storage_account.lake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "landing" {
  name               = "landing"
  storage_account_id = azurerm_storage_account.lake.id
}
