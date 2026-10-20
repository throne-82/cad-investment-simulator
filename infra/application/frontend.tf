resource "azurerm_container_app" "frontend" {
  name                         = "cad-frontend"
  resource_group_name          = var.config.application_resource_group_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  workload_profile_name        = "Consumption"
  revision_mode                = "Single"
  tags                         = local.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [var.config.pull_identity_id]
  }

  registry {
    server   = var.config.registry_login_server
    identity = var.config.pull_identity_id
  }

  template {
    min_replicas = 1
    max_replicas = 2

    http_scale_rule {
      name                = "http-concurrency"
      concurrent_requests = "50"
    }

    container {
      name   = "frontend"
      image  = var.frontend_image
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "BACKEND_ORIGIN"
        value = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
      }

      readiness_probe {
        transport        = "HTTP"
        port             = 8080
        path             = "/health"
        interval_seconds = 10
        timeout          = 2
      }

      liveness_probe {
        transport        = "HTTP"
        port             = 8080
        path             = "/health"
        initial_delay    = 10
        interval_seconds = 10
        timeout          = 2
      }
    }
  }

  ingress {
    external_enabled           = true
    allow_insecure_connections = false
    target_port                = 8080
    transport                  = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}

output "frontend_url" {
  value = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "backend_fqdn" {
  value = azurerm_container_app.backend.ingress[0].fqdn
}