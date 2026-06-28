resource "azurerm_container_app" "main" {
  name                         = "wallet-app"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = var.imported_resource_group_name
  revision_mode                = "Single"

  template {
    container {
      name   = "examplecontainerapp"
      image  = "mcr.microsoft.com/k8se/quickstart:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    target_port = 8080
    external    = true
  }
}