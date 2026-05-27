"""
STEP 2 — Prompt Builder
========================
Takes error logs + optional source code snippet
and builds a well-structured prompt for the LLM.

The better the prompt, the better Grok's analysis.
"""

import config


SYSTEM_PROMPT = """You are an expert DevOps engineer and software architect specialized in 
intelligent log analysis and root cause analysis. 

Your job is to:
1. Analyze error logs from production systems
2. Identify the root cause clearly and concisely
3. Assess the severity (CRITICAL / HIGH / MEDIUM / LOW)
4. Suggest the most likely fix
5. Detect if this is a real anomaly worth alerting on, or just noise

Always respond in this exact JSON format:
{
  "anomaly_detected": true or false,
  "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "component": "name of the affected component or service",
  "root_cause": "clear explanation of what went wrong",
  "suggested_fix": "specific actionable fix",
  "summary": "one line description for the alert notification"
}

Do not include anything outside the JSON. No markdown, no explanation."""


def build_prompt(error_logs: list, source_snippet: str = None):
    """
    Builds the full prompt to send to the LLM.

    Args:
        error_logs     : List of filtered error log entries
        source_snippet : Optional code around the error line (from GitHub)

    Returns:
        A dict with { "system": ..., "user": ... }
    """

    # Format logs into readable text
    log_text = _format_logs(error_logs)

    # Build the user message
    user_message = f"""
Analyze the following error logs from our {config.STACK.upper()} microservice 
running on ECS Fargate / CloudWatch:

=== ERROR LOGS ===
{log_text}
"""

    # Attach source code if available
    if source_snippet:
        user_message += f"""
=== SOURCE CODE (around the error line) ===
{source_snippet}
"""

    user_message += """
Based on the logs above, provide your analysis in the required JSON format.
"""

    print(f"[PromptBuilder] Prompt built with {len(error_logs)} error log(s).")
    if source_snippet:
        print("[PromptBuilder] Source code snippet included in prompt.")

    return {
        "system": SYSTEM_PROMPT,
        "user": user_message.strip()
    }


def _format_logs(error_logs: list) -> str:
    """Converts log list to clean readable text."""
    lines = []
    for i, log in enumerate(error_logs, 1):
        lines.append(
            f"[{i}] Timestamp : {log.get('timestamp', 'unknown')}\n"
            f"    Level     : {log.get('level', 'unknown')}\n"
            f"    Service   : {log.get('service', 'unknown')}\n"
            f"    Message   :\n{log.get('message', '')}\n"
        )
    return "\n".join(lines)


# ---- Quick test ----
if __name__ == "__main__":
    sample_logs = [
        {
            "timestamp": "2025-05-27T10:02:16Z",
            "level": "ERROR",
            "service": "ups-service",
            "message": "java.lang.NullPointerException: Cannot invoke method getId() on null object\n\tat com.company.ups.service.UserService.getUserById(UserService.java:89)"
        }
    ]

    prompt = build_prompt(sample_logs)
    print("=== SYSTEM PROMPT ===")
    print(prompt["system"])
    print("\n=== USER PROMPT ===")
    print(prompt["user"])
