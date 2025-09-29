# Oracle850B Infrastructure - Yandex Cloud
# Author: MagistrTheOne|Краснодар|2025

terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.100"
    }
  }
}

# Переменные
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

# Провайдер
provider "yandex" {
  token     = var.yc_token
  cloud_id  = var.yc_cloud_id
  folder_id = var.yc_folder_id
  zone      = var.zone
}

# VPC
resource "yandex_vpc_network" "oracle_network" {
  name = "${var.project_name}-network"
}

resource "yandex_vpc_subnet" "oracle_subnet" {
  name           = "${var.project_name}-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.oracle_network.id
  v4_cidr_blocks = ["10.0.0.0/24"]
}

# Object Storage для данных
resource "yandex_storage_bucket" "oracle_data" {
  bucket = "${var.project_name}-data"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    id      = "cleanup_old_versions"
    enabled = true
    
    expiration {
      days = 30
    }
  }
}

# Container Registry
resource "yandex_container_registry" "oracle_registry" {
  name = "${var.project_name}-registry"
}

# Kubernetes кластер для тренинга
resource "yandex_kubernetes_cluster" "oracle_training" {
  name = "${var.project_name}-training"
  
  network_id = yandex_vpc_network.oracle_network.id
  
  master {
    version = "1.28"
    zonal {
      zone      = var.zone
      subnet_id = yandex_vpc_subnet.oracle_subnet.id
    }
    
    public_ip = true
    
    maintenance_policy {
      auto_upgrade = true
    }
  }
  
  service_account_id      = yandex_iam_service_account.oracle_training.id
  node_service_account_id = yandex_iam_service_account.oracle_training.id
  
  depends_on = [
    yandex_resourcemanager_folder_iam_binding.oracle_training_editor,
    yandex_resourcemanager_folder_iam_binding.oracle_training_container_registry
  ]
}

# Node Group для тренинга
resource "yandex_kubernetes_node_group" "oracle_training_nodes" {
  cluster_id = yandex_kubernetes_cluster.oracle_training.id
  name       = "${var.project_name}-training-nodes"
  
  instance_template {
    platform_id = "gpu-standard-v3"
    
    resources {
      memory = 64
      cores  = 8
      gpus   = 1
    }
    
    boot_disk {
      type = "network-ssd"
      size = 100
    }
    
    network_interface {
      nat        = true
      subnet_ids = [yandex_vpc_subnet.oracle_subnet.id]
    }
    
    metadata = {
      ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
    }
  }
  
  scale_policy {
    fixed_scale {
      size = 8
    }
  }
  
  allocation_policy {
    locations = [var.zone]
  }
}

# Service Account для тренинга
resource "yandex_iam_service_account" "oracle_training" {
  name        = "${var.project_name}-training"
  description = "Service account for Oracle850B training"
}

# IAM роли
resource "yandex_resourcemanager_folder_iam_binding" "oracle_training_editor" {
  folder_id = var.yc_folder_id
  role      = "editor"
  
  members = [
    "serviceAccount:${yandex_iam_service_account.oracle_training.id}",
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "oracle_training_container_registry" {
  folder_id = var.yc_folder_id
  role      = "container-registry.images.puller"
  
  members = [
    "serviceAccount:${yandex_iam_service_account.oracle_training.id}",
  ]
}

# Бюджет и алерты
resource "yandex_billing_cloud_budget" "oracle_budget" {
  name = "${var.project_name}-budget"
  
  billing_account_id = var.yc_cloud_id
  
  budget_spec {
    amount {
      currency_code = "RUB"
      units         = tostring(var.budget_limit)
    }
    
    filter {
      service_ids = [
        "compute",
        "storage",
        "container-registry"
      ]
    }
    
    threshold_rules {
      threshold_percent = 50
      type              = "PERCENT"
    }
    
    threshold_rules {
      threshold_percent = 80
      type              = "PERCENT"
    }
    
    threshold_rules {
      threshold_percent = 100
      type              = "PERCENT"
    }
  }
  
  notification {
    type = "EMAIL"
    recipients {
      email = "admin@example.com"  # Заменить на реальный email
    }
  }
}

# Monitoring
resource "yandex_monitoring_dashboard" "oracle_dashboard" {
  title = "${var.project_name} Training Dashboard"
  
  labels = {
    service = "oracle850b"
  }
  
  widgets {
    title = "GPU Utilization"
    
    chart {
      queries {
        target {
          expr = "avg(gpu_utilization{service=\"oracle850b\"})"
        }
      }
    }
  }
  
  widgets {
    title = "Memory Usage"
    
    chart {
      queries {
        target {
          expr = "avg(memory_usage{service=\"oracle850b\"})"
        }
      }
    }
  }
}

# Outputs
output "cluster_id" {
  value = yandex_kubernetes_cluster.oracle_training.id
}

output "cluster_endpoint" {
  value = yandex_kubernetes_cluster.oracle_training.master[0].external_v4_endpoint
}

output "registry_id" {
  value = yandex_container_registry.oracle_registry.id
}

output "storage_bucket" {
  value = yandex_storage_bucket.oracle_data.bucket
}

output "network_id" {
  value = yandex_vpc_network.oracle_network.id
}
