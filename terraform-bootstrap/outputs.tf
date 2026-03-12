output "service_account_email" {
  description = "Email address of the cloud cost engine service account"
  value       = google_service_account.cost_engine_sa.email
}

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP region"
  value       = var.region
}

output "scheduler_invoker_service_account_email" {
  description = "Email address of Cloud Scheduler OIDC invoker identity"
  value       = google_service_account.scheduler_invoker_sa.email
}

output "github_deploy_service_account_email" {
  description = "Email address of GitHub Actions OIDC deploy identity"
  value       = google_service_account.github_deploy_sa.email
}

output "scheduler_job_name" {
  description = "Cloud Scheduler job name"
  value       = google_cloud_scheduler_job.cost_engine_scan.name
}

output "scan_endpoint" {
  description = "Authenticated scan endpoint target"
  value       = "${trimsuffix(data.google_cloud_run_service.cost_engine.status[0].url, "/")}/scan"
}

output "workload_identity_provider_resource_name" {
  description = "WIF provider resource name for GitHub secret GCP_WORKLOAD_IDENTITY_PROVIDER"
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}
