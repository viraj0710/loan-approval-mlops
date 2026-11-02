variable "kube_config_path" {
  description = "Path to the local kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Kubernetes context to use"
  type        = string
  default     = "minikube"
}

variable "namespace" {
  description = "Kubernetes namespace for the loan approval application"
  type        = string
  default     = "loan-app-tf"
}

variable "app_name" {
  description = "Label and base name for application resources"
  type        = string
  default     = "loan-approval-app"
}

variable "container_image" {
  description = "Docker image repository and tag for the loan approval container"
  type        = string
  default     = "loan-approval-mlops:latest"
}

variable "replicas" {
  description = "Number of deployment replica pods"
  type        = number
  default     = 2
}

variable "node_port_ui" {
  description = "NodePort allocated for Streamlit UI"
  type        = number
  default     = 30510
}

variable "node_port_metrics" {
  description = "NodePort allocated for Prometheus metrics exporter"
  type        = number
  default     = 30810
}
