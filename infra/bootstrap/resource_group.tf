resource "azurerm_resource_group" "bootstrap" {
  name     = "rg-cad-bootstrap-${local.suffix}"
  location = var.location
  tags     = var.tags
}

resource "azurerm_resource_group" "application" {
  name     = "rg-cad-application-${local.suffix}"
  location = var.location
  tags     = var.tags
}