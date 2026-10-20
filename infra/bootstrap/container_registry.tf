resource "azurerm_container_registry" "images" {
  name                = "cadacr${local.suffix}"
  resource_group_name = azurerm_resource_group.application.name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = var.tags
}