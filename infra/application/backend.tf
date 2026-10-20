resource "azurerm_container_app" "backend" {
  name                         = "cad-backend"
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
    max_replicas = 4

    http_scale_rule {
      name                = "http-concurrency"
      concurrent_requests = "2"
    }

    container {
      name   = "backend"
      image  = var.backend_image
      cpu    = 0.25
      memory = "0.5Gi"

      readiness_probe {
        transport        = "HTTP"
        port             = 8000
        path             = "/api/health"
        interval_seconds = 10
        timeout          = 2
      }

      liveness_probe {
        transport        = "HTTP"
        port             = 8000
        path             = "/api/health"
        initial_delay    = 10
        interval_seconds = 10
        timeout          = 2
      }
    }
  }

  ingress {
    external_enabled           = false
    allow_insecure_connections = false
    target_port                = 8000
    transport                  = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}