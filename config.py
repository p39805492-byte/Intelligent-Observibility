# ============================================================
#  Intelligent Observability — Config
#  Change settings here. Nothing else needs to be touched.
# ============================================================

# ------ LLM Provider ----------------------------------------
# Options: "grok" | "groq" | "openai" | "gemini"
LLM_PROVIDER = "grok"

# Drop your API key here when you have it
LLM_API_KEY = "YOUR_API_KEY_HERE"

# Provider base URLs (no need to change)
PROVIDER_URLS = {
    "grok":   "https://api.x.ai/v1/chat/completions",
    "groq":   "https://api.groq.com/openai/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}

# Provider models
PROVIDER_MODELS = {
    "grok":   "grok-3",
    "groq":   "llama-3.3-70b-versatile",
    "openai": "gpt-4o",
    "gemini": "gemini-2.0-flash",
}

# ------ App / Stack -----------------------------------------
# Options: "python" | "java" | "node" | "go" | "dotnet" | "ruby"
STACK = "java"

# ------ Log Settings ----------------------------------------
# For local testing we use dummy logs.
# For AWS: replace this with your CloudWatch log group name
LOG_SOURCE = "local"                        # "local" | "cloudwatch"
LOCAL_LOG_FILE = "dummy_logs/java_logs.json"
CLOUDWATCH_LOG_GROUP = "/ecs/ups-service"
LOG_FILTER_KEYWORDS = ["ERROR", "EXCEPTION", "FATAL", "WARN"]

# ------ GitHub / Source Code --------------------------------
GITHUB_ENABLED = True           # Set True when you share repo details
GITHUB_BASE_URL = "https://raw.githubusercontent.com"
GITHUB_REPO = "p39805492-byte/Intelligent-Observibility"                 # e.g. "your-org/your-repo"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = "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"                # Personal access token if private repo
CONTEXT_LINES = 10     

# ------ Alert / SNS -----------------------------------------
SNS_ENABLED = False              # Set True when on AWS
SNS_TOPIC_ARN = ""               # Your SNS ARN
ALERT_THRESHOLD = "ERROR"        # Minimum level to alert on

# ------ Local Run -------------------------------------------
LOCAL_MODE = True                # True = print alerts, no AWS calls
