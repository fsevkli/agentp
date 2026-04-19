"""
main.py Entry point for the multi-agent LLM penetration testing tool.

Usage:
    python main.py --target <IP> --scope <IP or CIDR>
"""

import json
import os
import argparse
from agents.orchestrator import orchestrate
from logger import init_logger


def main():
    parser = argparse.ArgumentParser(description="Multi-agent LLM penetration testing tool")
    parser.add_argument("--target", required=True, help="Target IP address")
    parser.add_argument("--scope", required=True, help="Allowed IP or CIDR subnet (e.g. 192.168.56.0/24)")
    args = parser.parse_args()

    os.makedirs("outputs", exist_ok=True)
    log_file = init_logger(args.target)
    print(f"Session log: {log_file}")

    result = orchestrate(args.target, args.scope)

    with open("outputs/shared_state.json", "w") as f:
        json.dump(result, f, indent=2)

    if result.get("report") and "error" not in result["report"]:
        with open("outputs/pentest_report.json", "w") as f:
            json.dump(result["report"], f, indent=2)
        print("[*] Report saved to outputs/pentest_report.json")

    print("\n=== Run Summary ===")
    print(f"Target : {result['target']}")
    print(f"Scope  : {result['scope']}")
    print(f"Status : {result['status']}")

    if result.get("errors"):
        for err in result["errors"]:
            print(f"  - {err}")
    else:
        rs = result.get("report", {}).get("risk_summary", {})
        if rs:
            print(f"Findings: Critical={rs.get('critical',0)}  High={rs.get('high',0)}  Medium={rs.get('medium',0)}  Low={rs.get('low',0)}")
        print("Full state saved to outputs/shared_state.json")


if __name__ == "__main__":
    main()
