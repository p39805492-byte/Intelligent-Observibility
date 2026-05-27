"""
STEP 1 — Log Fetcher
====================
Reads logs from local dummy files (for testing) or CloudWatch (for AWS).
Filters only ERROR / EXCEPTION / FATAL lines so Grok only sees relevant stuff.
"""

import json
import re
import config


def fetch_error_logs():
    """
    Main entry point.
    Returns a list of log entries that contain errors.
    """
    if config.LOG_SOURCE == "local":
        return _fetch_from_local_file()
    elif config.LOG_SOURCE == "cloudwatch":
        return _fetch_from_cloudwatch()
    else:
        raise ValueError(f"Unknown LOG_SOURCE: {config.LOG_SOURCE}")


def _fetch_from_local_file():
    """
    Reads dummy JSON log file and filters error logs.
    This simulates what CloudWatch would return.
    """
    print(f"[LogFetcher] Reading logs from: {config.LOCAL_LOG_FILE}")

    with open(config.LOCAL_LOG_FILE, "r") as f:
        all_logs = json.load(f)

    # Filter only error-level logs
    error_logs = [
        log for log in all_logs
        if any(keyword in log.get("level", "").upper() for keyword in config.LOG_FILTER_KEYWORDS)
        or any(keyword in log.get("message", "").upper() for keyword in config.LOG_FILTER_KEYWORDS)
    ]

    print(f"[LogFetcher] Total logs: {len(all_logs)} | Errors found: {len(error_logs)}")
    return error_logs


def _fetch_from_cloudwatch():
    """
    Fetches logs from AWS CloudWatch.
    Only runs when LOG_SOURCE = "cloudwatch" in config.
    Needs: pip install boto3 + AWS credentials configured.
    """
    import boto3
    from datetime import datetime, timedelta

    client = boto3.client("logs")

    # Fetch logs from the last 5 minutes
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)

    response = client.filter_log_events(
        logGroupName=config.CLOUDWATCH_LOG_GROUP,
        startTime=start_time,
        endTime=end_time,
        filterPattern="ERROR"
    )

    # Normalize to same format as local logs
    error_logs = []
    for event in response.get("events", []):
        error_logs.append({
            "timestamp": str(event["timestamp"]),
            "level": "ERROR",
            "service": config.CLOUDWATCH_LOG_GROUP.split("/")[-1],
            "message": event["message"]
        })

    print(f"[LogFetcher] CloudWatch errors found: {len(error_logs)}")
    return error_logs


# ---- Quick test ----
if __name__ == "__main__":
    logs = fetch_error_logs()
    print("\n--- FILTERED ERROR LOGS ---")
    for log in logs:
        print(f"[{log['timestamp']}] {log['level']}: {log['message'][:100]}...")
