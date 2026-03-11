# Deployment Guide

This guide deploys the full **Cloud Optimization Engine** stack:
- Scanner API on Cloud Run (`app/`)
- IAM, Workload Identity Federation, and Cloud Scheduler (`terraform-bootstrap/`)
- Optional demo resources for scan validation (`terraform/`)

## 1. Prerequisites

- Google Cloud SDK (`gcloud`) installed and authenticated
- Terraform `>= 1.5`
- Docker (for local image build/push)
- A GCP project with billing enabled

Set environment variables:

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export SERVICE_NAME="cloud-cost-engine"
export IMAGE_NAME="dockerhub_user/cloud-optimization-engine"
```

Point `gcloud` to the target project:

```bash
gcloud config set project "$PROJECT_ID"
```

Enable required services:

```bash
gcloud services enable run.googleapis.com compute.googleapis.com secretmanager.googleapis.com cloudscheduler.googleapis.com iam.googleapis.com cloudresourcemanager.googleapis.com
```

## 2. Create Slack Secret

Create the Secret Manager secret used by Cloud Run:

```bash
printf '%s' 'https://hooks.slack.com/services/XXX/YYY/ZZZ' | gcloud secrets create slack-webhook-url --data-file=-
```

If it already exists, add a new version:

```bash
printf '%s' 'https://hooks.slack.com/services/XXX/YYY/ZZZ' | gcloud secrets versions add slack-webhook-url --data-file=-
```

## 3. Deploy Cloud Run Service

Build and push the app image:

```bash
docker build -t "$IMAGE_NAME:latest" ./app
docker push "$IMAGE_NAME:latest"
```

Deploy service:

```bash
gcloud run deploy "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --platform=managed \
  --image="$IMAGE_NAME:latest" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-secrets="SLACK_WEBHOOK_URL=slack-webhook-url:latest"
```

## 4. Provision IAM, Scheduler, and GitHub OIDC

Create `terraform-bootstrap/terraform.tfvars`:

```hcl
project_id           = "your-gcp-project-id"
region               = "us-central1"
cloud_run_service_name = "cloud-cost-engine"
github_repository    = "OWNER/REPO"
```

Apply bootstrap infrastructure:

```bash
cd terraform-bootstrap
terraform init
terraform apply
cd ..
```

This creates:
- `cloud-cost-engine-sa`
- `cloud-scheduler-invoker-sa`
- `github-deploy-sa`
- GitHub Workload Identity Provider
- Scheduler job calling `GET /scan` on Cloud Run with OIDC

Re-deploy Cloud Run to run with the dedicated runtime service account:

```bash
gcloud run deploy "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --platform=managed \
  --image="$IMAGE_NAME:latest" \
  --service-account="cloud-cost-engine-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-secrets="SLACK_WEBHOOK_URL=slack-webhook-url:latest"
```

## 5. Optional: Deploy Demo Idle Resources

Use this only if you want predictable scanner findings for testing.

Create `terraform/terraform.tfvars`:

```hcl
project_id = "your-gcp-project-id"
```

Apply:

```bash
cd terraform
terraform init
terraform apply
cd ..
```

## 6. Configure GitHub Actions (CI/CD)

Set repository secrets used by `.github/workflows/deploy.yml`:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER` (from `terraform-bootstrap` output)
- `GCP_DEPLOY_SERVICE_ACCOUNT` (from `terraform-bootstrap` output)

Then push to `main` (or run workflow manually) to build image and deploy Cloud Run.

## 7. Verify Deployment

Health endpoint:

```bash
curl "$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')/"
```

Trigger scan manually:

```bash
curl "$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')/scan"
```

Check logs:

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="cloud-cost-engine"' --limit=50
```

## 8. Troubleshooting

Use [docs/troubleshooting.md](./troubleshooting.md) for known issues and fixes:
- Secret injection errors
- Scheduler `401 Unauthorized`
- GitHub OIDC auth problems
- Empty scan results
