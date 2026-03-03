import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from scanners.compute import scan_stopped_instances
from scanners.disks import scan_unattached_disks
from scanners.addresses import scan_unused_static_ips

# Initialize Slack client
slack_token = os.getenv('SLACK_WEBHOOK_URL')
slack_client = WebClient(slack_token)

# Scanner functions

def scan_vms():
    project_id = os.getenv('GCP_PROJECT_ID')
    return scan_stopped_instances(project_id)


def scan_disks():
    project_id = os.getenv('GCP_PROJECT_ID')
    return scan_unattached_disks(project_id)


def scan_ips():
    project_id = os.getenv('GCP_PROJECT_ID')
    return scan_unused_static_ips(project_id)

# Main orchestration

def run_scans():
    findings = {
        'vms': scan_vms(),
        'disks': scan_disks(),
        'ips': scan_ips()
    }
    
    # Aggregate and send report
    try:
        message = f"🔍 Cloud Optimization Scan Results\n\n"
        message += f"📊 Summary:\n"
        message += f"• Stopped VMs: {len(findings['vms'])}\n"
        message += f"• Unattached Disks: {len(findings['disks'])}\n"
        message += f"• Unused Static IPs: {len(findings['ips'])}\n\n"
        
        if findings['vms']:
            message += f"🖥️ Stopped VMs:\n"
            for vm in findings['vms']:
                message += f"  • {vm['name']} ({vm['zone']})\n"
        
        if findings['disks']:
            message += f"💾 Unattached Disks:\n"
            for disk in findings['disks']:
                message += f"  • {disk['name']} ({disk['zone']}) - {disk['size_gb']}GB\n"
        
        if findings['ips']:
            message += f"🌐 Unused Static IPs:\n"
            for ip in findings['ips']:
                message += f"  • {ip['name']} ({ip['region']}) - {ip['ip_address']}\n"
        
        slack_client.chat_postMessage(
            channel='#cloud-optimization',
            text=message
        )
    except SlackApiError as e:
        print(f'Slack error: {e}')

if __name__ == '__main__':
    run_scans()
