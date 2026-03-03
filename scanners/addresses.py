from google.cloud import compute_v1

def scan_unused_static_ips(project_id):
    client = compute_v1.AddressesClient()
    aggregated = client.aggregated_list(project=project_id)
    unused_ips = []
    
    for region, response in aggregated:
        if response.addresses:
            for address in response.addresses:
                if not address.allocated:
                    unused_ips.append({
                        "name": address.name,
                        "region": region.split('/')[-1],
                        "ip_address": address.ip_address,
                        "subnetwork": address.subnetwork.split('/')[-1] if address.subnetwork else None
                    })
    
    return unused_ips
