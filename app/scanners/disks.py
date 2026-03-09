from google.cloud import compute_v1

def scan_unattached_disks(project_id: str):
    client = compute_v1.DisksClient()
    aggregated = client.aggregated_list(project=project_id)

    unattached_disks = []

    for zone, response in aggregated:
        if response.disks:
            for disk in response.disks:
                if not disk.users:
                    unattached_disks.append({
                        "name": disk.name,
                        "zone": zone.split("/")[-1],
                        "size_gb": disk.size_gb
                    })

    return unattached_disks
