"""
scanner.py — Active recon tool: nmap port scanner

Wraps the nmap command-line tool and returns its output as a structured dict.
Called by the recon agent via LLM function calling.

Flags used:
  -sV  detect service versions (e.g. "vsftpd 2.3.4")
  -O   attempt OS fingerprinting
"""

import subprocess


def run_nmap(target: str) -> dict:
    """
    Run an nmap scan against the target and return the raw output.

    Returns a dict with the command, return code, stdout, and stderr
    so the LLM can read and interpret the full nmap output.
    """
    cmd = ["nmap", "-sV", "-O", target]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120  # nmap can be slow on targets with many filtered ports
    )

    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
