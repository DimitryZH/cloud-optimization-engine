import os
import logging
from flask import Flask, jsonify
from slack_sdk.webhook import WebhookClient
from scanners.compute import scan_stopped_instances
from scanners.disks import scan_unattached_disks
from scanners.addresses import scan_unused_static_ips


# -----------------------------------------------------------------------------
# Basic Logging Configuration (Cloud Run friendly)
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# -----------------------------------------------------------------------------
# Slack Webhook Initialization (via Secret Manager → env injection)
# -----------------------------------------------------------------------------
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
slack_client = WebhookClient(slack_webhook_url) if slack_webhook_url else None

if slack_client:
    logger.info("Slack webhook configured.")
else:
    logger.warning("Slack webhook not configured. Reports will not be sent.")


# -----------------------------------------------------------------------------
# Scanner Wrappers
# -----------------------------------------------------------------------------
def scan_vms():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    logger.info("Scanning for stopped VM instances...")
    return scan_stopped_instances(project_id)


def scan_disks():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    logger.info("Scanning for unattached disks...")
    return scan_unattached_disks(project_id)


def scan_ips():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    logger.info("Scanning for unused static IPs...")
    return scan_unused_static_ips(project_id)


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------
def run_scans():
    logger.info("Starting cloud optimization scan...")

    findings = {
        "vms": scan_vms(),
        "disks": scan_disks(),
        "ips": scan_ips()
    }

    logger.info("Scan completed. Aggregating results.")

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


# -----------------------------------------------------------------------------
# Slack Message Builder
# -----------------------------------------------------------------------------
def build_slack_message(findings):
    message = "🔍 *Cloud Optimization Scan Results*\n\n"
    message += "📊 *Summary:*\n"
    message += f"• Stopped VMs: {len(findings['vms'])}\n"
    message += f"• Unattached Disks: {len(findings['disks'])}\n"
    message += f"• Unused Static IPs: {len(findings['ips'])}\n\n"

    if findings["vms"]:
        message += "🖥️ *Stopped VMs:*\n"
        for vm in findings["vms"]:
            message += f"• {vm['name']} ({vm['zone']})\n"
        message += "\n"

    if findings["disks"]:
        message += "💾 *Unattached Disks:*\n"
        for disk in findings["disks"]:
            message += f"• {disk['name']} ({disk['zone']}) - {disk['size_gb']}GB\n"
        message += "\n"

    if findings["ips"]:
        message += "🌐 *Unused Static IPs:*\n"
        for ip in findings["ips"]:
            message += f"• {ip['name']} ({ip['region']}) - {ip['ip_address']}\n"
        message += "\n"

    return message


# -----------------------------------------------------------------------------
# HTTP Endpoints
# -----------------------------------------------------------------------------
@app.route("/")
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "cloud-optimization-engine"
    })


@app.route("/scan")
def trigger_scan():
    findings = run_scans()
    return jsonify(findings)


# -----------------------------------------------------------------------------
# Local Execution (Cloud Run uses Gunicorn instead)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting local server on port {port}")
    app.run(host="0.0.0.0", port=port)