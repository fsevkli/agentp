import json
import argparse
from agents.orchestrator import orchestrate


def main():
    parser = argparse.ArgumentParser(
        description="Multi-agent LLM penetration testing tool (starter version)"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Target IP address"
    )

    parser.add_argument(
        "--scope",
        required=True,
        help="Allowed IP or subnet (e.g., 192.168.56.101 or 192.168.56.0/24)"
    )

    args = parser.parse_args()

    # Run orchestrator
    result = orchestrate(args.target, args.scope)

    # Save output to JSON
    with open("outputs/shared_state.json", "w") as f:
        json.dump(result, f, indent=2)

    # Print summary
    print("\n=== Run Summary ===")
    print(f"Target: {result['target']}")
    print(f"Scope: {result['scope']}")
    print(f"Status: {result['status']}")

    if result.get("errors"):
        print("Errors:")
        for err in result["errors"]:
            print(f"- {err}")
    else:
        print("Recon + analysis complete.")
        print("Results saved to outputs/shared_state.json")


if __name__ == "__main__":
    main()
