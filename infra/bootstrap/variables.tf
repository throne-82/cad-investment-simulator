variable "location" {
  description = "The Azure region to deploy resources into."
  type        = string
  default     = "canadacentral"
}

variable "tags" {
  description = "A map of tags to assign to resources."
  type        = map(string)
  default = {
    project     = "cad-investment-simulator"
    environment = "assessment"
    managed_by  = "terraform"
    owner       = "Arthur Santos"
  }
}
