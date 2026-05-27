# 🔭 Intelligent Observability
> AI-powered log analysis for any tech stack — Python, Java, Node, Go, .NET, Ruby

## What It Does
- Reads error logs from ECS Fargate / CloudWatch (or local dummy logs)
- Fetches the exact source code around the error from GitHub/VCS
- Sends logs + code to an LLM (Grok / Groq / OpenAI)
- LLM explains root cause, severity, and suggested fix
- Publishes smart alerts to SNS → Slack / PagerDuty / Email

---

## Quick Start (Local Testing)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API key in config.py
```python
LLM_API_KEY = "your-key-here"
LLM_PROVIDER = "grok"   # or "groq", "openai", "gemini"
```

### 3. Choose your stack and log file
```python
STACK = "java"                              # or "python", "node", "go"
LOCAL_LOG_FILE = "dummy_logs/java_logs.json"
```

### 4. Run it
```bash
python lambda_function.py
```

---

## Project Structure
```
intelligent-observability/
├── lambda_function.py    # Main orchestrator (5 steps)
├── log_fetcher.py        # Step 1: Fetch & filter logs
├── prompt_builder.py     # Step 2: Build LLM prompt
├── llm_client.py         # Step 3: Call LLM API
├── alert_enricher.py     # Step 4: Add metadata
├── sns_publisher.py      # Step 5: Publish alert
├── stack_parser.py       # Extract file + line from stack trace
├── github_fetcher.py     # Fetch source code from GitHub/VCS
├── config.py             # All settings
├── dummy_logs/
│   ├── java_logs.json
│   ├── python_logs.json
│   └── node_logs.json
└── requirements.txt
```

---

## Supported Stacks
| Stack | Log Format Detected |
|-------|---------------------|
| Java Spring Boot | `at com.Class.method(File.java:89)` |
| Python Flask/Django | `File "/app/service.py", line 42` |
| Node.js / Express | `at handler (/app/routes.js:34:5)` |
| Go | `goroutine panic at main.go:56` |
| .NET / C# | `in /app/Service.cs:line 45` |
| Ruby on Rails | `/app/controller.rb:23` |

---

## Switching LLM Providers
Just change two lines in `config.py`:
```python
LLM_PROVIDER = "groq"          # grok | groq | openai | gemini
LLM_API_KEY  = "your-key"
```
Everything else works automatically.

---

## Enable GitHub Source Enrichment
```python
GITHUB_ENABLED  = True
GITHUB_REPO     = "your-org/your-repo"
GITHUB_BRANCH   = "main"
GITHUB_TOKEN    = "your-token"   # only needed for private repos
```

## Deploy to AWS Lambda
1. Zip all `.py` files
2. Upload to Lambda
3. Set `LOCAL_MODE = False` in config.py
4. Set `LOG_SOURCE = "cloudwatch"` in config.py
5. Add EventBridge schedule trigger (e.g., every 5 min)
6. Set SNS_ENABLED = True and SNS_TOPIC_ARN
