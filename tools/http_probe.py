"""
http_probe.py Active recon tool: HTTP header probe

Sends an HTTP HEAD request to the target using curl and returns the
response headers. Used to fingerprint the web server (e.g. Apache version,
PHP version, enabled security headers).

Called by the recon agent via LLM function calling.
"""

import subprocess


def run_curl(target: str) -> dict:
    """
    Send an HTTP HEAD request to the target and return the response headers.

    HEAD is used instead of GET to avoid downloading the response body —
    we only need the headers for fingerprinting purposes.
    """
    cmd = ["curl", "-I", "--max-time", "10", f"http://{target}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
