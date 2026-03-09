from google.cloud import compute_v1

def scan_unused_static_ips(project_id: str):
    client = compute_v1.AddressesClient()
    aggregated = client.aggregated_list(project=project_id)

    unused_ips = []

    for region, response in aggregated:
        if response.addresses:
            for address in response.addresses:
                if address.status == "RESERVED" and not address.users:
                    unused_ips.append({
                        "name": address.name,
                        "region": region.split("/")[-1],
                        "ip_address": address.address
                    })

    return unused_ips
