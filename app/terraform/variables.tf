variable "subscription_id" {
  type        = string
  description = "The Azure subscription ID"
  sensitive   = true
}

variable "created_resource_group_name" {
  type        = string
  description = "The name of the Resource Group to create"
  default     = "sisdis"
}

variable "location" {
  type        = string
  description = "The Azure Region to deploy resources"
  default     = "eastus2"
}

variable "imported_resource_group_name" {
  type        = string
  description = "The name of the imported Resource Group (used for Container App Environment and Container Apps)"
  default     = "pacocha-az"
}

variable "container_app_environment_name" {
  type        = string
  description = "The name of the Azure Container App Environment"
  default     = "managedEnvironment-pacochaaz-bd3b"
}

variable "key_vault_name" {
  type        = string
  description = "The name of the Azure Key Vault"
  default     = "Rodrygoleu7Komekito25"
}

variable "log_analytics_workspace_name" {
  type        = string
  description = "The name of the Log Analytics Workspace"
  default     = "log-analytics-workspace-sisdis"
}

variable "wallet_container_app_name" {
  type        = string
  description = "The name of the Container App in Azure"
  default     = "wallet-app"
}

variable "wallet_container_image_name" {
  type        = string
  description = "The name of the container image"
  default     = "wallet-container"
}

variable "tap_mock_container_app_name" {
  type        = string
  description = "The name of the Container App in Azure"
  default     = "tap-mock-app"
}

variable "tap_mock_container_image_name" {
  type        = string
  description = "The name of the container image"
  default     = "tap-mock-container"
}

variable "auth_container_app_name" {
  type        = string
  description = "The name of the Container App in Azure"
  default     = "auth-app"
}

variable "auth_container_image_name" {
  type        = string
  description = "The name of the container image"
  default     = "auth-container"
}

variable "github_secret_token_name" {
  type        = string
  description = "The name of the GitHub token to pull images from the GH registry"
  default = "github-token"
}

variable "github_secret_token" {
  type        = string
  description = "The GitHub token to pull images from the GH registry"
  sensitive   = true
}

variable "container_registry_server" {
  type        = string
  description = "the registry server name (we dont use azure container to store it)"
  default     = "ghcr.io"
}

variable "registry_username" {
  type        = string
  description = "the registry username (we dont use azure container to store it)"
  default     = "unsa-semester-2026-A"  
}