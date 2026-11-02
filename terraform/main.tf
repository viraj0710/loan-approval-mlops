resource "kubernetes_namespace" "loan_app" {
  metadata {
    name = var.namespace
    labels = {
      name                           = var.namespace
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
}

resource "kubernetes_deployment" "loan_app" {
  metadata {
    name      = "loan-approval-deployment"
    namespace = kubernetes_namespace.loan_app.metadata[0].name
    labels = {
      app                            = var.app_name
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    replicas = var.replicas

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_surge       = "1"
        max_unavailable = "0"
      }
    }

    selector {
      match_labels = {
        app = var.app_name
      }
    }

    template {
      metadata {
        labels = {
          app = var.app_name
        }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name              = "loan-approval-container"
          image             = var.container_image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http-ui"
            container_port = 8501
          }

          port {
            name           = "metrics"
            container_port = 8000
          }

          env {
            name  = "PYTHONUNBUFFERED"
            value = "1"
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/_stcore/health"
              port = 8501
            }
            initial_delay_seconds = 15
            period_seconds        = 10
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/_stcore/health"
              port = 8501
            }
            initial_delay_seconds = 8
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 2
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "loan_app" {
  metadata {
    name      = "loan-approval-service"
    namespace = kubernetes_namespace.loan_app.metadata[0].name
    labels = {
      app                            = var.app_name
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    type = "NodePort"
    selector = {
      app = var.app_name
    }

    port {
      name        = "http-ui"
      port        = 8501
      target_port = 8501
      node_port   = var.node_port_ui
    }

    port {
      name        = "metrics"
      port        = 8000
      target_port = 8000
      node_port   = var.node_port_metrics
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "loan_app" {
  metadata {
    name      = "loan-approval-hpa"
    namespace = kubernetes_namespace.loan_app.metadata[0].name
    labels = {
      app                            = var.app_name
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.loan_app.metadata[0].name
    }

    min_replicas = 2
    max_replicas = 5

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 75
        }
      }
    }
  }
}
