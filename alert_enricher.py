"""
STEP 4 — Alert Enricher
========================
Takes the raw LLM analysis and enriches it with metadata:
- timestamp
- log group
- provider
- stack type
- environment

This is what gets published to SNS / printed locally.
"""

from datetime import datetime
import config


def enrich_alert(llm_analysis: dict, error_logs: list):
    """
    Adds metadata to the LLM's raw analysis.

    Args:
        llm_analysis : The JSON dict returned by the LLM
        error_logs   : The original error logs (for reference)

    Returns:
        A fully enriched alert dict ready to publish.
    """
    if not llm_analysis:
        return None

    # Count errors by level
    level_counts = {}
    for log in error_logs:
        level = log.get("level", "UNKNOWN")
        level_counts[level] = level_counts.get(level, 0) + 1

    enriched = {
        # Core LLM analysis
        "anomaly_detected": llm_analysis.get("anomaly_detected", False),
        "severity":         llm_analysis.get("severity", "UNKNOWN"),
        "component":        llm_analysis.get("component", "unknown"),
        "root_cause":       llm_analysis.get("root_cause", ""),
        "suggested_fix":    llm_analysis.get("suggested_fix", ""),
        "summary":          llm_analysis.get("summary", ""),

        # Enriched metadata
        "metadata": {
            "timestamp":        datetime.utcnow().isoformat() + "Z",
            "log_group":        config.CLOUDWATCH_LOG_GROUP,
            "stack":            config.STACK,
            "llm_provider":     config.LLM_PROVIDER,
            "total_errors":     len(error_logs),
            "error_breakdown":  level_counts,
            "environment":      "local" if config.LOCAL_MODE else "aws",
        }
    }

    print(f"[AlertEnricher] Alert enriched → Severity: {enriched['severity']} | Component: {enriched['component']}")
    return enriched


# ---- Quick test ----
if __name__ == "__main__":
    import json

    mock_analysis = {
        "anomaly_detected": True,
        "severity": "HIGH",
        "component": "ups-service / UserService",
        "root_cause": "NullPointerException due to missing null check after DB query.",
        "suggested_fix": "Add null check before calling getId().",
        "summary": "[HIGH] NullPointerException in UserService.getUserById()"
    }

    mock_logs = [
        {"level": "ERROR", "message": "NullPointerException..."},
        {"level": "EXCEPTION", "message": "HttpClientErrorException..."}
    ]

    result = enrich_alert(mock_analysis, mock_logs)
    print("\n=== ENRICHED ALERT ===")
    print(json.dumps(result, indent=2))
