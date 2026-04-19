"""
dns_probe.py Passive recon tool: DNS lookup

Performs forward and reverse DNS lookups using Python's built-in socket
library. No external binary required.

This is passive recon — queries go to DNS servers, not the target directly.
Called by the recon agent via LLM function calling.
"""

import socket


def run_dns_lookup(target: str) -> dict:
    """
    Perform forward and reverse DNS lookups on the target.

    Returns a dict with reverse_dns, aliases, and forward_lookup fields.
    DNS lookups commonly fail for private IPs with no PTR record, so each
    lookup returns None on failure rather than crashing the pipeline.
    """
    try:
        hostname = socket.gethostbyaddr(target)
        reverse_dns = hostname[0]
        aliases = hostname[1]
    except socket.herror:
        reverse_dns = None
        aliases = []

    try:
        forward_ip = socket.gethostbyname(target)
    except socket.gaierror:
        forward_ip = None

    return {
        "reverse_dns": reverse_dns,
        "aliases": aliases,
        "forward_lookup": forward_ip
    }
