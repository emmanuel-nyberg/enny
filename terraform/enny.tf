provider "azurerm" {
    version = "~>2.11"
    features {}
}
resource "azurerm_resource_group" "enny" {
    name = "enny_resource_group"
    location = "North Europe"
}
resource "azurerm_postgresql_server" "ennydb" {
    name = "ennydb"
    resource_group_name = "enny_resource_group"
    location = "North Europe"
    sku_name = "B_Gen5_1"
    version = "10"
    administrator_login = "postgres"
    # Obviously not a real password
    administrator_login_password = "53cr37"
    ssl_enforcement_enabled = false
    storage_mb            = 5120
    backup_retention_days = 7
}
resource "azurerm_postgresql_database" "ennydb" {
    name    = "enny"
    resource_group_name = azurerm_resource_group.enny.name
    server_name         = azurerm_postgresql_server.ennydb.name
    charset             = "UTF8"
    collation           = "English_United States.1252"
}
resource "azurerm_app_service_plan" "enny" {
  name                = "enny-appserviceplan"
  kind                         = "Linux"
  reserved = true
  location            = azurerm_resource_group.enny.location
  resource_group_name = azurerm_resource_group.enny.name

  sku {
    tier = "Standard"
    size = "S1"
  }
}
resource "azurerm_app_service" "ennyapp" {
  name                = "enny-app-service"
  location            = azurerm_resource_group.enny.location
  resource_group_name = azurerm_resource_group.enny.name
  app_service_plan_id = azurerm_app_service_plan.enny.id

  site_config {
      linux_fx_version = "DOCKER|gasell.azurecr.io/enny:latest"
      app_command_line = "bash /app/start.sh"
  }

  app_settings = {
    "ENNY_DB_HOST" = azurerm_postgresql_server.ennydb.fqdn
    "ENNY_DB_USER" = azurerm_postgresql_server.ennydb.administrator_login
    "ENNY_DB_PASSWORD" = azurerm_postgresql_server.ennydb.administrator_login_password
    "ENNY_APIKEY" = "03VY6PIQ0F7QP4KE"
  }
}
