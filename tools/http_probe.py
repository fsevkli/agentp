import subprocess


def run_curl(target: str) -> dict:
    """
    Sends a basic HTTP HEAD request with curl.
    """
    url = f"http://{target}"

    cmd = ["curl", "-I", "--max-time", "10", url]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=20
    )

    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
