"""
vuln_agent.py Agent 3: Vulnerability Analyst

Responsibilities:
- Receive structured recon findings from Agent 2.
- Reason about each open port and service version to identify known
  vulnerabilities, misconfigurations, and attack surfaces.
- Map findings to CVE identifiers and CWE categories.
- Assign severity ratings (Critical / High / Medium / Low / Info).
- Return a structured list of vulnerabilities with evidence and attack vectors.
"""

import json
import re
import anthropic
from dotenv import load_dotenv
from logger import log_llm_call

load_dotenv()
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a vulnerability analyst in a penetration testing pipeline operating inside an authorised lab environment.
You receive structured reconnaissance findings and map them to known vulnerability classes.

Return a JSON object with EXACTLY this structure — no markdown, no extra keys:
{
  "vulnerabilities": [
    {
      "id": "<V-01, V-02, ...>",
      "title": "<short title>",
      "service": "<service name>",
      "port": <int or null>,
      "severity": "<Critical|High|Medium|Low|Info>",
      "cve_category": "<e.g. CVE-2011-2523, CWE-287, or category name>",
      "evidence": "<what in the recon data supports this>",
      "attack_vector": "<how an attacker would exploit this>"
    }
  ],
  "attack_surface_summary": "<paragraph summarising the overall attack surface>",
  "highest_risk": "<title of the single most dangerous finding>"
}

Use few-shot reasoning: for each open port and service, consider what known vulnerabilities or misconfigurations are associated with that version, then decide severity based on exploitability and impact."""

FEW_SHOT = """Example input fragment: {"open_ports": [{"port": 21, "service": "ftp", "version": "vsftpd 2.3.4"}]}
Example reasoning: vsftpd 2.3.4 contains a backdoor (CVE-2011-2523) that opens a shell on port 6200 when a smiley face is appended to the username. This is Critical severity."""


def run_vuln_analysis(recon: dict) -> dict:
    messages = [
        {
            "role": "user",
            "content": f"{FEW_SHOT}\n\nNow analyse these recon findings:\n{json.dumps(recon, indent=2)}"
        }
    ]

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=messages
    )

    content = next(b for b in response.content if b.type == "text").text
    log_llm_call("vuln_agent", messages, content)
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(match.group())
