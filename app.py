import os
import logging
from flask import Flask, jsonify
from slack_sdk.webhook import WebhookClient
from scanners.compute import scan_stopped_instances
from scanners.disks import scan_unattached_disks
from scanners.addresses import scan_unused_static_ips

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
slack_client = WebhookClient(slack_webhook_url) if slack_webhook_url else None

if slack_client:
    logger.info("Slack webhook configured.")
else:
    logger.warning("Slack webhook not configured. Reports will not be sent.")

def run_scans(project_id):
    logger.info(f"Starting cloud optimization scan for project: {project_id}")
    findings = {
        "vms": scan_stopped_instances(project_id),
        "disks": scan_unattached_disks(project_id),
        "ips": scan_unused_static_ips(project_id)
    }

    total_findings = (
        len(findings["vms"]) +
        len(findings["disks"]) +
        len(findings["ips"])
    )

    if slack_client:
        try:
            message = build_slack_message(findings)
            slack_client.send(text=message)
            logger.info("Slack notification sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")

    logger.info(f"Total findings detected: {total_findings}")
    return findings

def build_slack_message(findings):
    message = "🔍 *Cloud Optimization Scan Results*\n\n"
    message += "📊 *Summary:*\n"
    message += f"• Stopped VMs: {len(findings['vms'])}\n"
    message += f"• Unattached Disks: {len(findings['disks'])}\n"
    message += f"• Unused Static IPs: {len(findings['ips'])}\n\n"

    return message

@app.route("/")
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "cloud-optimization-engine"
    })

@app.route("/scan")
def trigger_scan():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    findings = run_scans(project_id)
    return jsonify(findings)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting local server on port {port}")
    app.run(host="0.0.0.0", port=port)
