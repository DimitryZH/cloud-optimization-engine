variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "REPLACE_WITH_PROJECT_ID"
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "sa_email" {
  description = "Service account email address"
  type        = string
  default     = "REPLACE_WITH_SERVICE_ACCOUNT_ID"
}

variable "cloud_run_service_name" {
  description = "Existing Cloud Run service name"
  type        = string
  default     = "REPLACE_WITH_CLOUD_RUN_SERVICE_NAME"
}

variable "scheduler_job_name" {
  description = "Cloud Scheduler job name"
  type        = string
  default     = "REPLACE_WITH_SCHEDULER_JOB_NAME"
}

variable "scheduler_cron" {
  description = "Cron schedule used by Cloud Scheduler"
  type        = string
  default     = "0 9 * * *"
}

variable "scheduler_time_zone" {
  description = "Cloud Scheduler job timezone"
  type        = string
  default     = "America/Toronto"
}

variable "github_repository" {
  description = "GitHub repository allowed to impersonate the deploy service account (owner/repo)"
  type        = string
  default     = "OWNER/REPO"
}
