"""
logger.py LLM call logger

Records every LLM interaction to a timestamped JSON file in the
logs/ directory. Provides a full audit trail of the pipeline run.
"""

import json
import os
from datetime import datetime

_log_file = None


def init_logger(target: str) -> str:
    global _log_file
    os.makedirs("logs", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    _log_file = f"logs/run_{ts}.json"
    with open(_log_file, "w") as f:
        json.dump({"target": target, "started": ts, "calls": []}, f, indent=2)
    return _log_file


def log_llm_call(agent: str, messages: list, response: str, tool_calls: list = None):
    if not _log_file:
        return
    with open(_log_file, "r") as f:
        data = json.load(f)
    data["calls"].append({
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
        "messages": messages,
        "response": response,
        "tool_calls": tool_calls or []
    })
    with open(_log_file, "w") as f:
        json.dump(data, f, indent=2)
