"""
Intelligent Observability — Main Lambda Handler
===============================================
Orchestrates all 5 steps:
  1. Fetch & filter error logs
  2. Build LLM prompt (+ optional GitHub source enrichment)
  3. Call LLM (Grok / Groq / OpenAI)
  4. Enrich alert with metadata
  5. Publish to SNS (or print locally)

Run locally:
  python lambda_function.py

Run on AWS Lambda:
  Deploy this file + all others. Handler = lambda_function.handler
"""

import json
import config
from log_fetcher    import fetch_error_logs
from stack_parser   import extract_error_location
from github_fetcher import fetch_source_snippet
from prompt_builder import build_prompt
from llm_client     import call_llm
from alert_enricher import enrich_alert
from sns_publisher  import publish_alert


def handler(event=None, context=None):
    """
    Main entry point.
    AWS Lambda calls handler(event, context).
    Local runs call handler() with no args.
    """
    print("\n" + "="*60)
    print("🚀 Intelligent Observability — Starting Analysis")
    print("="*60)

    # ── STEP 1: Fetch & filter error logs ──────────────────────
    print("\n📥 STEP 1: Fetching error logs...")
    error_logs = fetch_error_logs()

    if not error_logs:
        print("✅ No errors found in logs. All clear!")
        return {"status": "no_errors"}

    # ── STEP 2a: Extract error location (file + line) ──────────
    print("\n🔍 STEP 2a: Extracting error location from stack trace...")
    source_snippet = None

    # Use first error log to extract location
    first_error_message = error_logs[0].get("message", "")
    location = extract_error_location(first_error_message)

    # ── STEP 2b: Fetch source code from GitHub (if enabled) ────
    if location and config.GITHUB_ENABLED:
        print("\n📂 STEP 2b: Fetching source code from GitHub...")
        source_snippet = fetch_source_snippet(
            file_path  = location["file"],
            error_line = location["line"]
        )

    # ── STEP 2c: Build the LLM prompt ─────────────────────────
    print("\n📝 STEP 2: Building LLM prompt...")
    prompt = build_prompt(error_logs, source_snippet)

    # ── STEP 3: Call the LLM ──────────────────────────────────
    print(f"\n🤖 STEP 3: Calling {config.LLM_PROVIDER.upper()}...")
    llm_analysis = call_llm(prompt)

    if not llm_analysis:
        print("❌ LLM call failed. Exiting.")
        return {"status": "llm_error"}

    # ── STEP 4: Enrich alert with metadata ────────────────────
    print("\n📊 STEP 4: Enriching alert...")
    enriched_alert = enrich_alert(llm_analysis, error_logs)

    # ── STEP 5: Publish alert ─────────────────────────────────
    print("\n📢 STEP 5: Publishing alert...")
    publish_alert(enriched_alert)

    print("\n✅ Analysis complete!\n")
    return {"status": "success", "alert": enriched_alert}


# ── Local runner ──────────────────────────────────────────────
if __name__ == "__main__":
    result = handler()

    if result.get("alert"):
        print("\n📦 Final Alert Object (JSON):")
        print(json.dumps(result["alert"], indent=2))
