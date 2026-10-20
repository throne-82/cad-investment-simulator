terraform {
  required_version = ">= 1.6.5, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 4.81.0"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}

  subscription_id                 = var.config.subscription_id
  resource_provider_registrations = "none"
  storage_use_azuread             = true
}