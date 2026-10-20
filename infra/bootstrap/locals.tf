locals {
  suffix = substr(
    sha256(data.azurerm_client_config.current.subscription_id),
    0,
    8
  )
}