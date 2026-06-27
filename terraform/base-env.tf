resource "azurerm_log_analytics_workspace" "main" {
  name                = "Rodrygoleu7Komekito25-workspace"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "main" {
  name                       = "enviroment-sisdis"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  logs_destination           = "azure-monitor"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}