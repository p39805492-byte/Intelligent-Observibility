"""
STEP 3 — LLM Client
====================
Sends the prompt to whichever LLM provider is configured.
Supports: Grok, Groq, OpenAI, Gemini (all use same OpenAI-compatible API format).

Just change LLM_PROVIDER and LLM_API_KEY in config.py — nothing else changes.
"""

import json
import requests
import config


def call_llm(prompt: dict):
    """
    Sends the prompt to the LLM and returns parsed JSON analysis.

    Args:
        prompt: { "system": "...", "user": "..." }

    Returns:
        Dict with LLM analysis (anomaly_detected, severity, root_cause, etc.)
    """
    provider = config.LLM_PROVIDER
    api_key = config.LLM_API_KEY

    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        print("[LLMClient] ⚠️  No API key set. Running in MOCK mode.")
        return _mock_response()

    url = config.PROVIDER_URLS.get(provider)
    model = config.PROVIDER_MODELS.get(provider)

    if not url or not model:
        raise ValueError(f"[LLMClient] Unknown provider: {provider}")

    print(f"[LLMClient] Calling {provider.upper()} → model: {model}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": prompt["system"]},
            {"role": "user",   "content": prompt["user"]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("[LLMClient] ❌ Request timed out.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[LLMClient] ❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[LLMClient] ❌ Request failed: {e}")
        return None

    # Parse the response
    data = response.json()
    raw_text = data["choices"][0]["message"]["content"].strip()

    print(f"[LLMClient] ✅ Response received from {provider.upper()}")

    # Clean up and parse JSON
    return _parse_llm_json(raw_text)


def _parse_llm_json(raw_text: str):
    """Safely parses the LLM's JSON response."""
    # Strip markdown code fences if present
    clean = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(clean)
        return result
    except json.JSONDecodeError as e:
        print(f"[LLMClient] ⚠️  Failed to parse JSON: {e}")
        print(f"[LLMClient] Raw response was:\n{raw_text}")
        return {
            "anomaly_detected": True,
            "severity": "HIGH",
            "component": "unknown",
            "root_cause": raw_text,
            "suggested_fix": "Manual review required",
            "summary": "LLM response was not valid JSON — manual review needed"
        }


def _mock_response():
    """
    Returns a realistic mock response when no API key is set.
    So you can test the full pipeline without a key.
    """
    print("[LLMClient] 🎭 Returning MOCK LLM response for testing")
    return {
        "anomaly_detected": True,
        "severity": "HIGH",
        "component": "ups-service / UserService",
        "root_cause": (
            "NullPointerException on line 89 of UserService.java indicates that "
            "getUserById() is receiving a null user object, likely because the "
            "database query returned no result and the null check is missing before "
            "calling getId()."
        ),
        "suggested_fix": (
            "Add a null check after the DB call: "
            "if (user == null) throw new UserNotFoundException(id). "
            "Also check if the user ID being passed from the controller is valid."
        ),
        "summary": "[HIGH] NullPointerException in UserService.getUserById() — missing null check after DB query"
    }


# ---- Quick test ----
if __name__ == "__main__":
    sample_prompt = {
        "system": "You are a DevOps expert. Return JSON only.",
        "user": "Analyze this error: java.lang.NullPointerException at UserService.java:89"
    }

    result = call_llm(sample_prompt)
    print("\n=== LLM ANALYSIS ===")
    print(json.dumps(result, indent=2))
