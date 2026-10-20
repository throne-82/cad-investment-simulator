output "configuration" {
  value = {
    location                        = var.location
    application_resource_group_name = azurerm_resource_group.application.name
    registry_name                   = azurerm_container_registry.images.name
    registry_login_server           = azurerm_container_registry.images.login_server
    pull_identity_id                = azurerm_user_assigned_identity.pull.id
    deployment_client_id            = azurerm_user_assigned_identity.deployment.client_id
    tenant_id                       = data.azurerm_client_config.current.tenant_id
    subscription_id                 = data.azurerm_client_config.current.subscription_id
    state_resource_group_name       = azurerm_resource_group.bootstrap.name
    state_storage_account_name      = azurerm_storage_account.state.name
  }
}