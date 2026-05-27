"""
STEP 2a — GitHub / VCS Source Code Fetcher
===========================================
Given a filename + line number (from StackParser),
fetches the actual source code from GitHub (or your internal VCS).
Slices ±10 lines around the error so Grok understands the context.

To enable: set GITHUB_ENABLED = True in config.py and fill in GITHUB_REPO.
"""

import requests
import config


def fetch_source_snippet(file_path: str, error_line: int):
    """
    Fetches source code from GitHub/VCS and returns ±CONTEXT_LINES around error_line.

    Args:
        file_path  : e.g. "UserService.java" or "com/company/ups/service/UserService.java"
        error_line : Line number where the error occurred

    Returns:
        A formatted string of the code snippet, or None if disabled/failed.
    """
    if not config.GITHUB_ENABLED:
        print("[GitHubFetcher] GitHub enrichment is disabled. Skipping.")
        return None

    if not config.GITHUB_REPO:
        print("[GitHubFetcher] GITHUB_REPO not set in config. Skipping.")
        return None

    # Build the raw file URL
    url = f"{config.GITHUB_BASE_URL}/{config.GITHUB_REPO}/{config.GITHUB_BRANCH}/{file_path}"

    headers = {}
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"token {config.GITHUB_TOKEN}"

    print(f"[GitHubFetcher] Fetching: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[GitHubFetcher] Failed to fetch source: {e}")
        return None

    # Split into lines and slice around the error
    lines = response.text.split("\n")
    start = max(0, error_line - config.CONTEXT_LINES - 1)
    end = min(len(lines), error_line + config.CONTEXT_LINES)

    snippet_lines = []
    for i, line in enumerate(lines[start:end], start=start + 1):
        # Mark the exact error line with an arrow
        marker = ">>>" if i == error_line else "   "
        snippet_lines.append(f"{marker} {i:4d} | {line}")

    snippet = "\n".join(snippet_lines)

    print(f"[GitHubFetcher] Successfully fetched {len(snippet_lines)} lines around line {error_line}")
    return snippet


def get_internal_vcs_snippet(file_path: str, error_line: int, vcs_base_url: str, token: str = None):
    """
    Same as above but for internal VCS (Gitea, Gitlab, Bitbucket, etc.)
    Just change the URL format below to match your internal system.

    Args:
        vcs_base_url: e.g. "https://git.yourcompany.com/raw"
        token       : Your internal access token
    """
    url = f"{vcs_base_url}/{config.GITHUB_REPO}/{config.GITHUB_BRANCH}/{file_path}"

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        lines = response.text.split("\n")
        start = max(0, error_line - config.CONTEXT_LINES - 1)
        end = min(len(lines), error_line + config.CONTEXT_LINES)

        snippet_lines = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            marker = ">>>" if i == error_line else "   "
            snippet_lines.append(f"{marker} {i:4d} | {line}")

        return "\n".join(snippet_lines)

    except requests.exceptions.RequestException as e:
        print(f"[InternalVCS] Failed to fetch source: {e}")
        return None


# ---- Quick test ----
if __name__ == "__main__":
    # This will skip because GITHUB_ENABLED = False by default
    result = fetch_source_snippet("UserService.java", 89)
    if result:
        print(result)
    else:
        print("GitHub fetching is disabled. Set GITHUB_ENABLED=True in config to enable.")
