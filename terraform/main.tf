provider "google" {
  project = var.project_id
  region  = var.region_primary
}

resource "google_compute_disk" "disk_ml_training_old" {
  name  = "disk-ml-training-old"
  zone  = "us-central1-a"
  size  = 200
  type  = "pd-standard"
}

resource "google_compute_disk" "disk_backup_temp" {
  name  = "disk-backup-temp"
  zone  = "us-central1-b"
  size  = 100
  type  = "pd-standard"
}

resource "google_compute_disk" "disk_dev_scratch" {
  name  = "disk-dev-scratch"
  zone  = "us-central1-c"
  size  = 50
  type  = "pd-standard"
}

resource "google_compute_address" "ip_frontend_reserved" {
  name   = "ip-frontend-reserved"
  region = var.region_primary
}

resource "google_compute_address" "ip_legacy_nat" {
  name   = "ip-legacy-nat"
  region = var.region_secondary
}

resource "google_compute_instance" "vm_ci_runner_old" {
  name         = "vm-ci-runner-old"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    enable-oslogin = "TRUE"
    startup-script = <<-EOT
      #!/bin/bash
      sleep 20
      INSTANCE_NAME=$(curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name)
      ZONE=$(curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone | awk -F/ '{print $NF}')
      gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE
    EOT
  }

  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  scheduling {
    automatic_restart   = false
    on_host_maintenance = "MIGRATE"
  }
}

resource "google_compute_instance" "vm_test_env_paused" {
  name         = "vm-test-env-paused"
  machine_type = "e2-small"
  zone         = "europe-west1-b"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    enable-oslogin = "TRUE"
    startup-script = <<-EOT
      #!/bin/bash
      sleep 20
      INSTANCE_NAME=$(curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name)
      ZONE=$(curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone | awk -F/ '{print $NF}')
      gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE
    EOT
  }

  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  scheduling {
    automatic_restart   = false
    on_host_maintenance = "MIGRATE"
  }
}
