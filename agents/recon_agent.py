from tools.scanner import run_nmap
from tools.http_probe import run_curl


def run_recon(target: str) -> dict:
    """
    Runs real recon tools and returns structured findings.
    """
    nmap_output = run_nmap(target)
    curl_output = run_curl(target)

    return {
        "nmap": nmap_output,
        "curl": curl_output
    }
