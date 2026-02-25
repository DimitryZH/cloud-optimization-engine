output "disks" {
  value = [
    google_compute_disk.disk_ml_training_old.name,
    google_compute_disk.disk_backup_temp.name,
    google_compute_disk.disk_dev_scratch.name
  ]
}

output "static_ips" {
  value = [
    google_compute_address.ip_frontend_reserved.address,
    google_compute_address.ip_legacy_nat.address
  ]
}

output "vms" {
  value = [
    google_compute_instance.vm_ci_runner_old.name,
    google_compute_instance.vm_test_env_paused.name
  ]
}
