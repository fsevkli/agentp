"""
report_agent.py Agent 4: Report Writer

Responsibilities:
- Receive the full shared state (recon + vulnerability findings).
- Synthesise all findings into a professional penetration test report.
- Produce per-finding remediation advice, risk ratings, and an
  executive summary suitable for a non-technical audience.
- Return a structured JSON report ready to be saved as the final deliverable.
"""

import json
import re
import anthropic
from dotenv import load_dotenv
from logger import log_llm_call

load_dotenv()
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a professional penetration testing report writer.
Synthesise recon findings and vulnerability analysis into a structured pen-test report.

Return a JSON object with EXACTLY this structure — no markdown, no extra keys:
{
  "executive_summary": "<2-3 sentence non-technical summary for management>",
  "scope": "<target and boundaries tested>",
  "methodology": "<brief description of tools and techniques used>",
  "findings": [
    {
      "id": "<matches vuln id>",
      "title": "<short title>",
      "severity": "<Critical|High|Medium|Low|Info>",
      "description": "<what the vulnerability is>",
      "evidence": "<specific data from the scan supporting this finding>",
      "remediation": "<concrete steps to fix>",
      "risk_rating": "<CVSS-style justification>"
    }
  ],
  "risk_summary": {
    "critical": <int>,
    "high": <int>,
    "medium": <int>,
    "low": <int>,
    "info": <int>
  },
  "conclusion": "<overall security posture assessment>",
  "recommendations": ["<prioritised action item>"]
}"""


def run_report(state: dict) -> dict:
    payload = {
        "target": state.get("target"),
        "scope": state.get("scope"),
        "recon": state.get("recon", {}),
        "vulnerabilities": state.get("vulnerabilities", {})
    }

    messages = [
        {
            "role": "user",
            "content": f"Generate a penetration test report. Include only the top 10 most critical findings and keep each field concise:\n{json.dumps(payload, indent=2)}"
        }
    ]

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=messages
    )

    content = next(b for b in response.content if b.type == "text").text
    log_llm_call("report_agent", messages, content)
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(match.group())
