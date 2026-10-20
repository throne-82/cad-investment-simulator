variable "config" {
  description = "Infrastructure identifiers created by bootstrap."
  type = object({
    subscription_id                 = string
    location                        = string
    application_resource_group_name = string
    registry_login_server           = string
    pull_identity_id                = string
  })
}

variable "backend_image" {
  description = "Full backend image reference, tagged by commit SHA."
  type        = string
}

variable "frontend_image" {
  description = "Full frontend image reference, tagged by commit SHA."
  type        = string
}