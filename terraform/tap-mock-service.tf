resource "azurerm_container_app" "tap_mock" {
  name                         = var.tap_mock_container_app_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = var.imported_resource_group_name
  revision_mode                = "Single"

  template {
    container {
      name   = var.tap_mock_container_app_name
      image  = "mcr.microsoft.com/k8se/quickstart:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true   
    target_port                = 8000       
    transport                  = "auto"
    
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  identity {
    type = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.user_assigned_identity.id]
  }
  
  secret {
    name = var.github_secret_token_name
    identity = azurerm_user_assigned_identity.user_assigned_identity.id
    key_vault_secret_id = azurerm_key_vault_secret.github_secret_token.id 
  }

  registry {
    server = var.container_registry_server
    username = var.registry_username
    password_secret_name = var.github_secret_token_name
  }

  lifecycle {
    ignore_changes = [
      secret,
    ]
  }
}
