import ipaddress
from agents.recon_agent import run_recon


def in_scope(target: str, scope: str) -> bool:
    """
    Returns True if the target is within the allowed scope.
    Supports:
    - exact IP match: 192.168.56.101
    - CIDR subnet: 192.168.56.0/24
    """
    try:
        target_ip = ipaddress.ip_address(target)

        if "/" in scope:
            network = ipaddress.ip_network(scope, strict=False)
            return target_ip in network

        return target_ip == ipaddress.ip_address(scope)

    except ValueError:
        return False


def orchestrate(target: str, scope: str) -> dict:
    """
    Main controller for the first project phase.
    """
    state = {
        "target": target,
        "scope": scope,
        "status": "",
        "recon": {},
        "errors": []
    }

    if not in_scope(target, scope):
        state["status"] = "rejected_out_of_scope"
        state["errors"].append(f"Target {target} is outside allowed scope {scope}.")
        return state

    state["status"] = "approved_in_scope"

    try:
        recon_results = run_recon(target)
        state["recon"] = recon_results
        state["status"] = "recon_complete"
    except Exception as e:
        state["status"] = "recon_failed"
        state["errors"].append(str(e))

    return state
