#!/usr/bin/env python3
import json
import os
import re
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8765
BASE_DIR = Path(__file__).resolve().parent

PROFILE_PATH = BASE_DIR / "profile_schema.json"
RULES_PATH = BASE_DIR / "matching_rules.md"

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_prompt(page: dict) -> str:
    profile = load_text(PROFILE_PATH)
    rules = load_text(RULES_PATH)

    return f"""
You are Jay Job Matcher.

Your task is to evaluate a job posting against Jay's verified portfolio/career profile.
Do NOT match by title alone.
Translate portfolio evidence into the language of the JD.
Do NOT invent achievements, metrics, seniority, tools, or experience.

PROFILE JSON:
{profile}

MATCHING RULES:
{rules}

JOB PAGE TITLE:
{page.get('title','')}

JOB URL:
{page.get('url','')}

VISIBLE JOB PAGE TEXT:
{page.get('text','')[:50000]}

Return ONLY valid JSON with this exact shape:
{{
  "company": "string",
  "position": "string",
  "score": 0,
  "grade": "A|B|DISCARD",
  "jd_structure": {
    "primary_hiring_intent": "string",
    "weighted_subtasks": [
      {
        "subtask": "string",
        "weight": "CRITICAL|HIGH|MEDIUM|LOW",
        "evidence_from_jd": "string"
      }
    ],
    "repeated_signals": ["string"],
    "high_salience_phrases": ["string"],
    "special_submission_requirements": ["string"],
    "likely_first_6_month_outputs": ["string"],
    "background_filters": ["string"],
    "hard_eligibility": ["string"],
    "preferences": ["string"]
  },
  "score_breakdown": {{
    "capability_fit": 0,
    "role_transferability": 0,
    "environment_fit": 0,
    "gap_cost": 0
  }},
  "top_matches": [
    {{
      "jd_requirement": "string",
      "matched_capability": "string",
      "evidence": "string"
    }}
  ],
  "strongest_match": {
    "title": "short Korean title for the single strongest intersection between this JD and Jay",
    "portfolio_cv_connection": "name the exact project/CV evidence that best proves it",
    "why_it_matters": "1-3 sentences explaining why this is the most important overlap"
  },
  "main_gap": "string",
  "gap_interpretation": "string",
  "fatal_gap": false,
  "action": "APPLY TODAY|APPLY|REVIEW|SKIP",
  "summary_ko": "Korean summary in 3-6 concise sentences"
}}

Rules:
- A = 80+ and no fatal gap.
- B = 70-79 and no fatal gap.
- DISCARD = below 70 or fatal gap.
- top_matches must contain only the strongest 3 or 4 matches.
- score_breakdown maximums are 40, 25, 20, 15.
- score must equal the sum of those four numbers.
- Be strict. Vague words like creativity or communication do not count without evidence.
- Do NOT score before structurally reading the JD.
- Weight repeated responsibilities, top-listed responsibilities, ownership verbs, concrete deliverables, and special submission requirements more heavily.
- Treat special submission requirements as strong evidence of what the company actually values.
- Do not over-penalize broad industry-background requirements when they are not supported by the actual responsibility structure.
- strongest_match must identify ONE decisive intersection, not a generic capability list.
- strongest_match must explicitly name the portfolio project or CV evidence that proves it.
- Prefer the overlap that is both highly salient in the JD and unusually well evidenced in Jay's portfolio.
"""


def call_anthropic(prompt: str) -> dict:
    if not API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Run: export ANTHROPIC_API_KEY='your_api_key'"
        )

    payload = {
        "model": MODEL,
        "max_tokens": 2200,
        "temperature": 0.1,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic API error {e.code}: {body}") from e

    blocks = raw.get("content", [])
    text_parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    output = "\n".join(text_parts).strip()

    # tolerate accidental markdown fences
    output = re.sub(r"^\s*\`\`\`(?:json)?\s*", "", output, flags=re.I)
    output = re.sub(r"\s*\`\`\`\s*$", "", output)

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", output)
        if not m:
            raise RuntimeError("Model did not return valid JSON.")
        return json.loads(m.group(0))


def format_report(result: dict, source_url: str) -> str:
    top = result.get("top_matches", [])
    lines = [
        f"{result.get('company','')} — {result.get('position','')}",
        "",
        f"{result.get('grade','')} GRADE · {result.get('score',0)}%",
        "",
        "WHY THIS FITS",
    ]

    for i, item in enumerate(top, 1):
        lines.append(
            f"{i}. {item.get('jd_requirement','')}\n"
            f"   → {item.get('matched_capability','')}\n"
            f"   → {item.get('evidence','')}"
        )

    lines += [
        "",
        "MAIN GAP",
        result.get("main_gap", ""),
        "",
        "GAP INTERPRETATION",
        result.get("gap_interpretation", ""),
        "",
        "ACTION",
        result.get("action", ""),
        "",
        result.get("summary_ko", ""),
        "",
        f"Source: {source_url}",
    ]

    return "\n".join(lines)


class Handler(BaseHTTPRequestHandler):
    def _headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.end_headers()

    def do_OPTIONS(self):
        self._headers(204)

    def do_GET(self):
        if self.path == "/health":
            self._headers(200)
            self.wfile.write(json.dumps({
                "ok": True,
                "service": "Jay Job Matcher",
                "model": MODEL,
                "api_key_set": bool(API_KEY)
            }).encode("utf-8"))
            return

        self._headers(404)
        self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        if self.path != "/analyze":
            self._headers(404)
            self.wfile.write(b'{"error":"not found"}')
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            page = json.loads(body)

            if not page.get("text"):
                raise RuntimeError("No visible page text received.")

            result = call_anthropic(build_prompt(page))
            result["source_url"] = page.get("url", "")
            result["report"] = format_report(result, page.get("url", ""))

            self._headers(200)
            self.wfile.write(json.dumps(
                result,
                ensure_ascii=False
            ).encode("utf-8"))

        except Exception as e:
            self._headers(500)
            self.wfile.write(json.dumps({
                "error": str(e)
            }, ensure_ascii=False).encode("utf-8"))

    def log_message(self, fmt, *args):
        print("[Jay Job Matcher]", fmt % args)


if __name__ == "__main__":
    print(f"Jay Job Matcher running at http://{HOST}:{PORT}")
    print(f"Model: {MODEL}")
    print("Health check: http://127.0.0.1:8765/health")
    if not API_KEY:
        print("")
        print("WARNING: ANTHROPIC_API_KEY is not set.")
        print("Set it first:")
        print("  export ANTHROPIC_API_KEY='your_api_key'")
        print("")
    HTTPServer((HOST, PORT), Handler).serve_forever()
