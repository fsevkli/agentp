"""
whois_probe.py Passive recon tool: whois lookup

Queries the whois database to gather network ownership and registration
information about the target IP. This is passive recon — no packets are
sent to the target itself.

Called by the recon agent via LLM function calling.
"""

import subprocess


def run_whois(target: str) -> dict:
    """
    Perform a whois lookup on the target IP or domain.

    Returns a dict with the command, return code, stdout, and stderr.
    """
    cmd = ["whois", target]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
