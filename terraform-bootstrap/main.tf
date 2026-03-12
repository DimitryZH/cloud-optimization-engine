provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "current" {
  project_id = var.project_id
}

data "google_cloud_run_service" "cost_engine" {
  name     = var.cloud_run_service_name
  location = var.region
}

resource "google_service_account" "cost_engine_sa" {
  account_id   = "cloud-cost-engine-sa"
  display_name = "Cloud Cost Engine Service Account"
}

resource "google_service_account" "scheduler_invoker_sa" {
  account_id   = "cloud-scheduler-invoker-sa"
  display_name = "Cloud Scheduler Invoker"
}

resource "google_service_account" "github_deploy_sa" {
  account_id   = "github-deploy-sa"
  display_name = "GitHub CI/CD Deploy Service Account"
}

resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
  description               = "OIDC identities from GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub OIDC Provider"
  description                        = "Accept OIDC tokens issued by GitHub Actions"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  attribute_condition = "assertion.repository == \"${var.github_repository}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_project_iam_member" "cost_engine_roles" {
  project = var.project_id
  role    = "roles/compute.viewer"
  member  = "serviceAccount:cloud-cost-engine-sa@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cost_engine_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:cloud-cost-engine-sa@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cost_engine_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:cloud-cost-engine-sa@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cost_engine_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:cloud-cost-engine-sa@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cost_engine_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:cloud-cost-engine-sa@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "github_deploy_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_deploy_sa.email}"
}

resource "google_project_iam_member" "github_deploy_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_deploy_sa.email}"
}

resource "google_service_account_iam_member" "github_wif_workload_identity_user" {
  service_account_id = google_service_account.github_deploy_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repository}"
}

resource "google_cloud_run_service_iam_member" "scheduler_run_invoker" {
  project  = var.project_id
  location = var.region
  service  = data.google_cloud_run_service.cost_engine.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_invoker_sa.email}"
}

resource "google_service_account_iam_member" "scheduler_service_agent_actas" {
  service_account_id = google_service_account.scheduler_invoker_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
}

resource "google_cloud_scheduler_job" "cost_engine_scan" {
  name             = var.scheduler_job_name
  description      = "Trigger cloud-cost-engine /scan endpoint"
  schedule         = var.scheduler_cron
  time_zone        = var.scheduler_time_zone
  region           = var.region
  attempt_deadline = "320s"

  http_target {
    uri         = "${trimsuffix(data.google_cloud_run_service.cost_engine.status[0].url, "/")}/scan"
    http_method = "GET"

    oidc_token {
      service_account_email = google_service_account.scheduler_invoker_sa.email
      audience              = data.google_cloud_run_service.cost_engine.status[0].url
    }
  }

  depends_on = [
    google_cloud_run_service_iam_member.scheduler_run_invoker,
    google_service_account_iam_member.scheduler_service_agent_actas
  ]
}
