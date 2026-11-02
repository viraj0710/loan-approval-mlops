output "namespace" {
  description = "The namespace where the application is deployed"
  value       = kubernetes_namespace.loan_app.metadata[0].name
}

output "deployment_name" {
  description = "Name of the deployed Kubernetes deployment"
  value       = kubernetes_deployment.loan_app.metadata[0].name
}

output "service_name" {
  description = "Name of the deployed Kubernetes service"
  value       = kubernetes_service.loan_app.metadata[0].name
}

output "service_nodeport_ui" {
  description = "NodePort allocated for Streamlit UI"
  value       = kubernetes_service.loan_app.spec[0].port[0].node_port
}

output "service_nodeport_metrics" {
  description = "NodePort allocated for Prometheus metrics"
  value       = kubernetes_service.loan_app.spec[0].port[1].node_port
}
