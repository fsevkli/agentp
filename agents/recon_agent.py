"""
recon_agent.py Agent 2: Reconnaissance

Responsibilities:
- Perform passive recon: whois lookup, DNS resolution.
- Perform active recon: nmap port scan, curl HTTP probe.
- Use Claude tool use so the LLM decides which tools to invoke
  and interprets the raw results into structured JSON findings.
"""

import json
import re
import anthropic
from dotenv import load_dotenv
from tools.scanner import run_nmap
from tools.http_probe import run_curl
from tools.whois_probe import run_whois
from tools.dns_probe import run_dns_lookup
from logger import log_llm_call

load_dotenv()
client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "run_nmap",
        "description": "Active recon: run an nmap port scan with service and OS detection against the target IP.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "The IP address to scan"}
            },
            "required": ["target"]
        }
    },
    {
        "name": "run_curl",
        "description": "Active recon: send an HTTP HEAD request to probe the web server and capture response headers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "The IP address to probe"}
            },
            "required": ["target"]
        }
    },
    {
        "name": "run_whois",
        "description": "Passive recon: perform a whois lookup to gather registration and network ownership information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "The IP address or domain to look up"}
            },
            "required": ["target"]
        }
    },
    {
        "name": "run_dns_lookup",
        "description": "Passive recon: perform forward and reverse DNS lookups to identify hostnames and aliases.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "The IP address or hostname to resolve"}
            },
            "required": ["target"]
        }
    }
]

TOOL_MAP = {
    "run_nmap": run_nmap,
    "run_curl": run_curl,
    "run_whois": run_whois,
    "run_dns_lookup": run_dns_lookup
}

SYSTEM_PROMPT = """You are a reconnaissance agent in a penetration testing pipeline operating inside an authorised lab environment.
Perform both passive and active reconnaissance using all available tools:
- Passive: run_whois, run_dns_lookup
- Active: run_nmap, run_curl

You MUST call all four tools before returning your final answer.

After collecting all results, return a JSON object with EXACTLY this structure — no markdown, no extra keys:
{
  "open_ports": [{"port": <int>, "service": "<str>", "version": "<str>"}],
  "os_guess": "<str>",
  "web_server": "<str or null>",
  "http_headers": {"<header>": "<value>"},
  "whois_info": {"network_owner": "<str>", "country": "<str>", "registrar": "<str or null>"},
  "dns_info": {"reverse_dns": "<str or null>", "aliases": ["<str>"]},
  "raw_summary": "<one paragraph summarising all passive and active findings>"
}"""


def _serialize_content(content: list) -> list:
    result = []
    for block in content:
        if hasattr(block, "model_dump"):
            result.append(block.model_dump())
        elif isinstance(block, dict):
            result.append(block)
        else:
            result.append(str(block))
    return result


def run_recon(target: str) -> dict:
    messages = [
        {"role": "user", "content": f"Perform full passive and active reconnaissance on target: {target}"}
    ]

    for _ in range(10):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}
            }],
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_names = [b.name for b in response.content if b.type == "tool_use"]
            log_llm_call("recon_agent", messages, "", tool_names)

            messages.append({"role": "assistant", "content": _serialize_content(response.content)})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = TOOL_MAP[block.name](**block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            text_block = next(b for b in response.content if b.type == "text")
            log_llm_call("recon_agent", messages, text_block.text)
            match = re.search(r"\{.*\}", text_block.text, re.DOTALL)
            return json.loads(match.group())

    return {"error": "Recon agent exceeded max iterations"}
