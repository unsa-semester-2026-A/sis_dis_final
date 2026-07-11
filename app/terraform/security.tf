data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                        = var.key_vault_name
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions     = ["Get"]
    secret_permissions  = ["Get", "List", "Set", "Delete"]
    storage_permissions = ["Get"]
  }
# Permisos para el user_assigned_identity 
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_user_assigned_identity.user_assigned_identity.principal_id 

    secret_permissions = ["Get", "List"]
  }
}


resource "azurerm_key_vault_secret" "github_secret_token" {
  name         = var.github_secret_token_name
  value        = var.github_secret_token 
  key_vault_id = azurerm_key_vault.main.id     
}

resource "azurerm_user_assigned_identity" "user_assigned_identity" {
  location            = azurerm_resource_group.main.location
  name                = "user-assigned-identity"
  resource_group_name = azurerm_resource_group.main.name
}
