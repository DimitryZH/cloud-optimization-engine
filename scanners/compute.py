from google.cloud import compute_v1

def scan_stopped_instances(project_id: str):
    client = compute_v1.InstancesClient()
    aggregated = client.aggregated_list(project=project_id)

    stopped_instances = []

    for zone, response in aggregated:
        if response.instances:
            for instance in response.instances:
                if instance.status == "TERMINATED":
                    stopped_instances.append({
                        "name": instance.name,
                        "zone": zone.split("/")[-1],
                        "machine_type": instance.machine_type.split("/")[-1] if instance.machine_type else None
                    })

    return stopped_instances
