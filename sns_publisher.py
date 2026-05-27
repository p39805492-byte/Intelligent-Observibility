"""
STEP 5 — SNS Publisher
=======================
If anomaly detected → publishes the alert.
In LOCAL mode → pretty prints to terminal.
In AWS mode   → publishes to SNS topic (which can fan out to Slack, PagerDuty, email, etc.)
"""

import json
import config


def publish_alert(enriched_alert: dict):
    """
    Publishes the alert to SNS or prints it locally.

    Args:
        enriched_alert: The fully enriched alert dict from AlertEnricher.
    """
    if not enriched_alert:
        print("[SNSPublisher] No alert to publish.")
        return

    if not enriched_alert.get("anomaly_detected"):
        print("[SNSPublisher] ✅ No anomaly detected. No alert sent.")
        return

    severity  = enriched_alert.get("severity", "UNKNOWN")
    component = enriched_alert.get("component", "unknown")
    subject   = f"[{severity}] {component}"

    if config.LOCAL_MODE:
        _print_local_alert(enriched_alert, subject)
    else:
        _publish_to_sns(enriched_alert, subject)


def _print_local_alert(alert: dict, subject: str):
    """Pretty prints the alert for local testing."""
    separator = "=" * 60

    print(f"\n{separator}")
    print(f"🚨 ALERT: {subject}")
    print(separator)
    print(f"📍 Component   : {alert['component']}")
    print(f"⚡ Severity    : {alert['severity']}")
    print(f"🔍 Root Cause  : {alert['root_cause']}")
    print(f"🛠  Fix         : {alert['suggested_fix']}")
    print(f"\n📋 Summary     : {alert['summary']}")
    print(f"\n📊 Metadata:")
    for k, v in alert.get("metadata", {}).items():
        print(f"   {k:20} : {v}")
    print(separator)
    print(f"✅ Alert would publish to SNS topic: {config.SNS_TOPIC_ARN or 'NOT SET (local mode)'}")
    print(separator)


def _publish_to_sns(alert: dict, subject: str):
    """Publishes to AWS SNS. Only runs when SNS_ENABLED=True in config."""
    import boto3

    client = boto3.client("sns")

    message = json.dumps(alert, indent=2)

    response = client.publish(
        TopicArn=config.SNS_TOPIC_ARN,
        Subject=subject[:100],  # SNS subject max 100 chars
        Message=message
    )

    print(f"[SNSPublisher] ✅ Alert published to SNS | MessageId: {response['MessageId']}")
    return response


# ---- Quick test ----
if __name__ == "__main__":
    mock_alert = {
        "anomaly_detected": True,
        "severity": "HIGH",
        "component": "ups-service / UserService",
        "root_cause": "NullPointerException due to missing null check after DB query.",
        "suggested_fix": "Add null check before calling getId().",
        "summary": "[HIGH] NullPointerException in UserService.getUserById()",
        "metadata": {
            "timestamp": "2025-05-27T10:02:16Z",
            "log_group": "/ecs/ups-service",
            "stack": "java",
            "llm_provider": "grok",
            "total_errors": 3,
            "error_breakdown": {"ERROR": 2, "EXCEPTION": 1},
            "environment": "local"
        }
    }

    publish_alert(mock_alert)
