resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_workspace_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# IMPORTANT NOTES
# In the current implementation we dont use the resource group created on main (I hate the student account restrictions :/)
resource "azurerm_container_app_environment" "main" {
  #name                       = "container-app-enviroment-sisdis" 
  # here we using a previous environment created for testing purposes
  # and use this command before to 'terraform aply' terraform import azurerm_container_app_environment.main /subscriptions/SUBSCRIPTION_ID/resourceGroups/NOMBRE_DEL_RESOURCE_GROUP_VIEJO/providers/Microsoft.App/managedEnvironments/NOMBRE_DE_TU_ENTORNO_VIEJO
  name                       = var.container_app_environment_name
  location                   = azurerm_resource_group.main.location
  #resource_group_name       = azurerm_resource_group.main.name 
  resource_group_name        = var.imported_resource_group_name
  logs_destination           = "log-analytics"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}