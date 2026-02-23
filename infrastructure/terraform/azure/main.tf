terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }

  backend "azurerm" {
    resource_group_name  = "datapulse-terraform-rg"
    storage_account_name = "datapulseterraform"
    container_name       = "tfstate"
    key                  = "azure/terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "datapulse-${var.environment}-rg"
  location = var.azure_region

  tags = {
    Project     = "DataPulse"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "datapulse-aks-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "datapulse-${var.environment}"

  default_node_pool {
    name       = "default"
    node_count = var.environment == "production" ? 3 : 2
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
    network_policy = "calico"
  }
}

# Azure Container Registry
resource "azurerm_container_registry" "main" {
  name                = "datapulseacr${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.environment == "production" ? "Premium" : "Basic"
  admin_enabled       = true
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "datapulse-postgres-${var.environment}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  administrator_login    = "datapulse_admin"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = var.environment == "production" ? "GP_Standard_D2s_v3" : "B_Standard_B1ms"
  zone                   = "1"
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "datapulse"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Azure Cache for Redis
resource "azurerm_redis_cache" "main" {
  name                = "datapulse-redis-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 0
  family              = "C"
  sku_name            = var.environment == "production" ? "Standard" : "Basic"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
}

# Storage Account for reports
resource "azurerm_storage_account" "main" {
  name                     = "datapulsestore${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "production" ? "GRS" : "LRS"
}

resource "azurerm_storage_container" "reports" {
  name                  = "reports"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

variable "environment" {
  type    = string
  default = "staging"
}

variable "azure_region" {
  type    = string
  default = "East US"
}

variable "db_password" {
  type      = string
  sensitive = true
}
