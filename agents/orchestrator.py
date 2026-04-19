"""
orchestrator.py Agent 1: Orchestrator

Responsibilities:
- Validate the target against the defined scope (guardrail).
- Dispatch agents in sequence: Recon --> Vulnerability Analyst --> Report Writer.
- Pass the shared state dict between agents so findings flow downstream.
- Halt the pipeline and record the error if any agent fails.
"""

import ipaddress
from agents.recon_agent import run_recon
from agents.vuln_agent import run_vuln_analysis
from agents.report_agent import run_report


def in_scope(target: str, scope: str) -> bool:
    """
    Check whether the target IP is within the allowed scope.

    Supports two formats:
      - Exact IP:  "192.168.56.101"
      - CIDR subnet: "192.168.56.0/24"

    Returns False for any invalid input so the pipeline fails safely.
    """
    try:
        target_ip = ipaddress.ip_address(target)

        if "/" in scope:
            # Scope is a subnet check if the target falls within the range
            network = ipaddress.ip_network(scope, strict=False)
            return target_ip in network

        # Scope is a single IP must be an exact match
        return target_ip == ipaddress.ip_address(scope)

    except ValueError:
        # Invalid IP or subnet string — reject immediately
        return False


def orchestrate(target: str, scope: str) -> dict:
    """
    Main pipeline controller.

    Builds a shared state dict and passes it through each agent in order.
    Each agent reads from state and writes its findings back into it.
    If any agent fails, the error is recorded and the pipeline stops early.
    """

    # Shared state single source of truth passed through the entire pipeline
    state = {
        "target": target,
        "scope": scope,
        "status": "",
        "recon": {},           # filled by Agent 2 (Recon)
        "vulnerabilities": {}, # filled by Agent 3 (Vulnerability Analyst)
        "report": {},          # filled by Agent 4 (Report Writer)
        "errors": []
    }

    # Guardrail: reject out-of-scope targets before any agent runs
    if not in_scope(target, scope):
        state["status"] = "rejected_out_of_scope"
        state["errors"].append(f"Target {target} is outside allowed scope {scope}.")
        return state

    state["status"] = "approved_in_scope"
    print(f"Target in scope. Starting reconnaissance against {target}...")

    # Agent 2: Recon
    # Uses LLM function calling to run passive (whois, DNS) and
    # active (nmap, curl) recon tools, then returns structured JSON.
    try:
        state["recon"] = run_recon(target)
        state["status"] = "recon_complete"
        print("Recon complete.")
    except Exception as e:
        state["status"] = "recon_failed"
        state["errors"].append(f"Recon: {e}")
        return state  # no point continuing without recon data

    # Agent 3: Vulnerability Analyst
    # Receives recon findings and maps them to CVE/CWE categories
    # with severity ratings and attack vectors.
    print("Running vulnerability analysis...")
    try:
        state["vulnerabilities"] = run_vuln_analysis(state["recon"])
        state["status"] = "vuln_analysis_complete"
        print("Vulnerability analysis complete.")
    except Exception as e:
        state["status"] = "vuln_analysis_failed"
        state["errors"].append(f"Vuln analysis: {e}")
        return state  # no point writing a report without vulnerability data

    # --- Agent 4: Report Writer ---
    # Synthesises all findings into a structured pen-test report with
    # risk ratings, evidence, and remediation advice.
    print("Writing pen-test report...")
    try:
        state["report"] = run_report(state)
        state["status"] = "report_complete"
        print("Report complete.")
    except Exception as e:
        state["status"] = "report_failed"
        state["errors"].append(f"Report writer: {e}")

    return state
