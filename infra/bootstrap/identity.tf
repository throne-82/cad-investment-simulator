resource "azurerm_user_assigned_identity" "deployment" {
  name                = "id-cad-deployment"
  resource_group_name = azurerm_resource_group.bootstrap.name
  location            = var.location
  tags                = var.tags
}

resource "azurerm_user_assigned_identity" "pull" {
  name                = "id-cad-image-pull"
  resource_group_name = azurerm_resource_group.application.name
  location            = var.location
  tags                = var.tags
}

resource "azurerm_federated_identity_credential" "github" {
  name                      = "github-main"
  user_assigned_identity_id = azurerm_user_assigned_identity.deployment.id
  issuer                    = "https://token.actions.githubusercontent.com"
  audience                  = ["api://AzureADTokenExchange"]
  subject                   = "repo:throne-82/cad-investment-simulator:ref:refs/heads/main"
}


resource "azurerm_role_assignment" "local_state" {
  scope                = azurerm_storage_account.state.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "deployment_resources" {
  scope                            = azurerm_resource_group.application.id
  role_definition_name             = "Contributor"
  principal_id                     = azurerm_user_assigned_identity.deployment.principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "deployment_images" {
  scope                            = azurerm_container_registry.images.id
  role_definition_name             = "AcrPush"
  principal_id                     = azurerm_user_assigned_identity.deployment.principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "deployment_state" {
  scope                            = azurerm_storage_container.state["application"].id
  role_definition_name             = "Storage Blob Data Contributor"
  principal_id                     = azurerm_user_assigned_identity.deployment.principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "pull_images" {
  scope                            = azurerm_container_registry.images.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_user_assigned_identity.pull.principal_id
  skip_service_principal_aad_check = true
}