from google.cloud import compute_v1

def scan_unused_addresses(project_id):
    client = compute_v1.AddressesClient()
    aggregated = client.aggregated_list(project=project_id)

    unused = []

    for region, response in aggregated:
        if response.addresses:
            for address in response.addresses:
                if not address.users:
                    unused.append({
                        "name": address.name,
                        "region": region.split("/")[-1],
                        "address": address.address
                    })

    return unused
