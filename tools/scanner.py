import subprocess


def run_nmap(target: str) -> dict:
    """
    Runs an nmap scan and returns structured output.
    """
    cmd = ["nmap", "-sV", "-O", target]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120
    )

    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
