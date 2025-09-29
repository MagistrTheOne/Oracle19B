# Oracle850B Infrastructure Variables
# Author: MagistrTheOne|Краснодар|2025

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "oracle850b"
}

variable "yc_token" {
  description = "Yandex Cloud API token"
  type        = string
  sensitive   = true
}

variable "yc_cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
}

variable "yc_folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
}

variable "region" {
  description = "Yandex Cloud region"
  type        = string
  default     = "ru-central1"
}

variable "zone" {
  description = "Yandex Cloud zone"
  type        = string
  default     = "ru-central1-a"
}

variable "budget_limit" {
  description = "Monthly budget limit in RUB"
  type        = number
  default     = 100000
}

variable "gpu_node_count" {
  description = "Number of GPU nodes for training"
  type        = number
  default     = 8
}

variable "gpu_type" {
  description = "GPU type for training nodes"
  type        = string
  default     = "gpu-standard-v3"
}

variable "node_memory_gb" {
  description = "Memory per node in GB"
  type        = number
  default     = 64
}

variable "node_cores" {
  description = "CPU cores per node"
  type        = number
  default     = 8
}

variable "storage_size_gb" {
  description = "Storage size per node in GB"
  type        = number
  default     = 100
}

variable "admin_email" {
  description = "Admin email for budget alerts"
  type        = string
  default     = "admin@example.com"
}
