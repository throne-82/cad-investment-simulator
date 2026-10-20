resource "azurerm_log_analytics_workspace" "logs" {
  name                = "cad-investment-logs"
  resource_group_name = var.config.application_resource_group_name
  location            = var.config.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  daily_quota_gb      = 0.1
  tags                = local.tags
}