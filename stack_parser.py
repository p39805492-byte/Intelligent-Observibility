"""
Stack Parser
============
Extracts filename + line number from stack traces.
Works for Python, Java, Node.js, Go, .NET, Ruby.
This is what lets us fetch the exact source code from GitHub.
"""

import re
import config

# One regex per stack — captures filename and line number
STACK_PARSERS = {
    "python": r'File "(?P<file>[^"]+)", line (?P<line>\d+)',
    "java":   r'at [\w.$]+\((?P<file>\w+\.java):(?P<line>\d+)\)',
    "node":   r'at .+? \((?P<file>[^:]+):(?P<line>\d+):\d+\)',
    "go":     r'(?P<file>[^\s]+\.go):(?P<line>\d+)',
    "dotnet": r'in (?P<file>.+):line (?P<line>\d+)',
    "ruby":   r'(?P<file>[^\s]+\.rb):(?P<line>\d+)',
}


def extract_error_location(log_message: str):
    """
    Given a raw log message (stack trace), returns the first
    file + line number found, based on the configured STACK.

    Returns: { "file": "UserService.java", "line": 89 }
    or None if nothing found.
    """
    stack = config.STACK

    if stack not in STACK_PARSERS:
        print(f"[StackParser] Unknown stack: {stack}. Skipping source extraction.")
        return None

    pattern = STACK_PARSERS[stack]
    match = re.search(pattern, log_message)

    if match:
        result = {
            "file": match.group("file"),
            "line": int(match.group("line"))
        }
        print(f"[StackParser] Found error at → {result['file']} : line {result['line']}")
        return result

    print("[StackParser] Could not extract file/line from stack trace.")
    return None


# ---- Quick test ----
if __name__ == "__main__":
    # Test with a Java stack trace
    java_trace = """
    java.lang.NullPointerException: Cannot invoke method getId()
        at com.company.ups.service.UserService.getUserById(UserService.java:89)
        at com.company.ups.controller.UserController.getUser(UserController.java:45)
    """

    print("Testing Java parser:")
    print(extract_error_location(java_trace))

    # Test with a Python stack trace (temporarily switch stack)
    python_trace = """
    Traceback (most recent call last):
      File "/app/services/user_service.py", line 42, in get_user
        user_id = request.args['user_id']
    KeyError: 'user_id'
    """

    config.STACK = "python"
    print("\nTesting Python parser:")
    print(extract_error_location(python_trace))
