# la azurerm_resource_group es el tipo de recurso a crear
# main es el nombre del recurso dentro de terraform
# name es el nombre del recurso en azure
# location es la ubicacion del recurso en azure
resource "azurerm_resource_group" "main" {
  name     = "sisdis"
  location = "eastus2"
}