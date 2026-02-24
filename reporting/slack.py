import requests
import os

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")

def send_slack_report(summary, details):
    if not SLACK_WEBHOOK:
        return

    text = (
        "*GCP Cloud Cost Scanner Report*\n\n"
        f"Project: `{details['project']}`\n\n"
        "*Summary:*\n"
        f"• Stopped VM instances: {summary['stopped_instances_count']}\n"
        f"• Unattached disks: {summary['unattached_disks_count']}\n"
        f"• Unused static IPs: {summary['unused_static_ips_count']}\n"
    )

    payload = {"text": text}

    requests.post(SLACK_WEBHOOK, json=payload)
