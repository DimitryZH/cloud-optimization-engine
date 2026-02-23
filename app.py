from flask import Flask, jsonify
from scanners.compute import scan_stopped_instances
from scanners.disks import scan_unattached_disks
from scanners.addresses import scan_unused_addresses
from reporting.slack import send_slack_report
import os

app = Flask(__name__)

PROJECT_ID = os.environ.get("GCP_PROJECT")

@app.route("/")
def run_scan():
    if not PROJECT_ID:
        return jsonify({"error": "GCP_PROJECT environment variable not set"}), 500

    stopped = scan_stopped_instances(PROJECT_ID)
    disks = scan_unattached_disks(PROJECT_ID)
    ips = scan_unused_addresses(PROJECT_ID)

    summary = {
        "stopped_instances_count": len(stopped),
        "unattached_disks_count": len(disks),
        "unused_static_ips_count": len(ips)
    }

    details = {
        "project": PROJECT_ID,
        "stopped_instances": stopped,
        "unattached_disks": disks,
        "unused_static_ips": ips
    }

    send_slack_report(summary, details)

    return jsonify({
        "summary": summary,
        "details": details
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
