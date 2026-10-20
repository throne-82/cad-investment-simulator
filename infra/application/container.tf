resource "azurerm_container_app_environment" "main" {
  name                       = "cad-investment-environment"
  resource_group_name        = var.config.application_resource_group_name
  location                   = var.config.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
  tags                       = local.tags

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}