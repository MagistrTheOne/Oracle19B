# Oracle850B Infrastructure Outputs
# Author: MagistrTheOne|Краснодар|2025

output "cluster_id" {
  description = "Kubernetes cluster ID"
  value       = yandex_kubernetes_cluster.oracle_training.id
}

output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = yandex_kubernetes_cluster.oracle_training.master[0].external_v4_endpoint
}

output "cluster_ca_certificate" {
  description = "Kubernetes cluster CA certificate"
  value       = yandex_kubernetes_cluster.oracle_training.master[0].cluster_ca_certificate
  sensitive   = true
}

output "registry_id" {
  description = "Container registry ID"
  value       = yandex_container_registry.oracle_registry.id
}

output "registry_endpoint" {
  description = "Container registry endpoint"
  value       = yandex_container_registry.oracle_registry.registry_domain
}

output "storage_bucket" {
  description = "Object storage bucket name"
  value       = yandex_storage_bucket.oracle_data.bucket
}

output "network_id" {
  description = "VPC network ID"
  value       = yandex_vpc_network.oracle_network.id
}

output "subnet_id" {
  description = "VPC subnet ID"
  value       = yandex_vpc_subnet.oracle_subnet.id
}

output "service_account_id" {
  description = "Training service account ID"
  value       = yandex_iam_service_account.oracle_training.id
}

output "budget_id" {
  description = "Budget ID for cost monitoring"
  value       = yandex_billing_cloud_budget.oracle_budget.id
}
