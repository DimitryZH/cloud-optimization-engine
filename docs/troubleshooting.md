# Troubleshooting Guide - Cloud Optimization Engine 

This document captures real issues encountered during development and their solutions.

It reflects real-world debugging scenarios across Cloud Run, IAM, Terraform, CI/CD, and GCP APIs.

## 1. Secret Injection Issue

### Problem

Slack webhook was not injected into Cloud Run correctly.

### Cause

Incorrect Secret Manager name or wrong --set-secrets flag during deployment.

### Solution

Verify secret exists:

```bash
gcloud secrets list
```

Deploy with correct flag:

```bash
--set-secrets=SLACK_WEBHOOK_URL=slack-webhook-url:latest
```

Ensure runtime service account has:

roles/secretmanager.secretAccessor

## 2. Compute API Invalid Request (aggregated_list)

### Error

ValueError: Invalid request. Required field: project

### Cause

project_id was not properly passed to Compute API.

### Solution

Use Cloud Run built-in environment variable:

```python
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
```

Pass explicitly:

```python
client.aggregated_list(project=project_id)
```

## 3. 'MapComposite' Object Is Not Callable

### Error

TypeError: 'MapComposite' object is not callable

### Cause

Incorrect iteration over aggregated results.

### Incorrect

```python
for zone, scoped_list in aggregated():
```

### Correct

```python
for zone, scoped_list in aggregated.items():
```

## 4. Cloud Run Worker Timeout

### Error

WORKER TIMEOUT

Worker was sent SIGKILL! Perhaps out of memory?

### Cause

Gunicorn worker blocking or insufficient memory allocation.

### Solution

- Reduced workers to 1
- Configured threads
- Verified memory settings in Cloud Run
- Ensured scanner logic does not block application startup

Example:

```bash
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
```

## 5. Cloud Scheduler 401 Unauthorized

### Problem

Scheduler could not invoke /scan.

### Cause

Missing roles/run.invoker for scheduler service account.

### Solution

Grant permission:

```bash
gcloud run services add-iam-policy-binding cloud-cost-engine \
  --member="serviceAccount:cloud-scheduler-invoker-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

Ensure scheduler job uses OIDC token.

## 6. CI/CD Authentication Issues

### Problem

GitHub Actions could not authenticate to GCP.

### Cause

Incorrect Workload Identity Federation configuration.

### Solution

Ensure:

- Workload Identity Pool exists
- Provider is configured
- roles/iam.workloadIdentityUser granted to GitHub principal

GitHub workflow uses:

```yaml
permissions:
  id-token: write
```

And:

```yaml
uses: google-github-actions/auth@v2
```

## 7. Terraform Drift (Manual IAM Changes)

### Problem

IAM roles were added manually outside Terraform.

### Risk

Infrastructure not reproducible.

### Solution

Reconcile cloud state:

```bash
gcloud projects get-iam-policy PROJECT_ID
```

Add missing bindings into terraform-bootstrap.

Make Terraform the source of truth.

## 8. Docker Image Too Large

### Problem

Dockerfile in root copied entire repository into image.

### Impact

Large image size and slower CI/CD builds.

### Solution

Refactor repository:

```text
app/
    Dockerfile
    app.py
    requirements.txt
    scanners/
```

Update GitHub Actions:

```yaml
context: ./app
```

Add proper .dockerignore.

## 9. Slack Not Receiving Messages

### Symptoms

Scan works but Slack report not received.

### Possible Causes

- Secret not injected
- Missing IAM permission
- Invalid webhook URL

### Verification

Check Cloud Run logs:

```bash
gcloud logging read \
'resource.type="cloud_run_revision" AND resource.labels.service_name="cloud-cost-engine"' \
--limit=50
```

## 10. Scanner Returns Empty Results

### Scenario

```json
{"disks": [], "ips": [], "vms": []}
```

### Cause

No demo infrastructure deployed.

### Solution

Run:

```bash
terraform apply
```

Provision test VMs, disks, IPs.

## 11. Dynamic Validation Experiment

To validate detection logic:

- Increase VM count in Terraform
- Run terraform apply
- Wait for scheduled execution
- Compare Slack reports

This confirms:

- Scanner reacts to infrastructure changes
- Scheduler automation works
- End-to-end pipeline is functional

## Lessons Learned

- Always reconcile IAM before Terraform apply
- Use OIDC federation for CI/CD
- Use least-privilege service accounts
- Keep Docker build context minimal
- Make Terraform the source of truth
- Validate infrastructure dynamically, not statically

## Final System Status

+ Cloud Run deployed via CI/CD
+ OIDC authentication configured
+ Scheduler securely invoking /scan
+ Terraform-managed IAM
+ Slack reporting operational
+ Modular scanner architecture validated

This document reflects real debugging and hardening experience during the implementation of the Cloud Optimization Engine.
