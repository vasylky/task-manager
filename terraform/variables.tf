# variables.tf
variable "resource_group_name" {
  description = "Name of the resource group"
  default     = "task-manager-rg"
}

variable "location" {
  description = "Azure location"
  default     = "East US 2"

}

variable "acr_name" {
  description = "Name of the Azure Container Registry"
  default     = "taskmanageracr37857348"
}

variable "aks_name" {
  description = "Name of the Azure Kubernetes Service"
  default     = "task-manager-aks"
}

variable "mysql_server_name" {
  description = "Name of the MySQL server"
  default     = "task-manager-mysql"
}

variable "mysql_admin_login" {
  description = "MySQL admin login"
  default     = "mysqladmin"
}

variable "mysql_admin_password" {
  description = "MySQL admin password"
  sensitive   = true
}