#!/usr/bin/env python3
import csv
import html
import json
import os
import re
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8765
BASE_DIR = Path(__file__).resolve().parent

PROFILE_PATH = BASE_DIR / "profile_schema.json"
RULES_PATH = BASE_DIR / "matching_rules.md"

# 분석 기록 저장 위치 (이 폴더 안 history/)
HISTORY_DIR = BASE_DIR / "history"
HISTORY_JSONL = HISTORY_DIR / "matches.jsonl"
HISTORY_CSV = HISTORY_DIR / "matches.csv"
HISTORY_HTML = HISTORY_DIR / "index.html"

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
  "jd_structure": {{
    "primary_hiring_intent": "string",
    "weighted_subtasks": [
      {{
        "subtask": "string",
        "weight": "CRITICAL|HIGH|MEDIUM|LOW",
        "evidence_from_jd": "string"
      }}
    ],
    "repeated_signals": ["string"],
    "high_salience_phrases": ["string"],
    "special_submission_requirements": ["string"],
    "likely_first_6_month_outputs": ["string"],
    "background_filters": ["string"],
    "hard_eligibility": ["string"],
    "preferences": ["string"]
  }},
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
  "strongest_match": {{
    "title": "short Korean title for the single strongest intersection between this JD and Jay",
    "portfolio_cv_connection": "name the exact project/CV evidence that best proves it",
    "why_it_matters": "1-3 sentences explaining why this is the most important overlap"
  }},
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
        "max_tokens": 4000,
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


# ---------- history ----------

def _slim(result: dict) -> dict:
    """차트에 필요한 필드만 남긴 기록 한 줄."""
    b = result.get("score_breakdown") or {}
    sm = result.get("strongest_match") or {}
    return {
        "analyzed_at": result.get("analyzed_at") or datetime.now().isoformat(timespec="seconds"),
        "company": result.get("company", ""),
        "position": result.get("position", ""),
        "url": result.get("source_url", ""),
        "score": result.get("score", 0),
        "grade": result.get("grade", ""),
        "action": result.get("action", ""),
        "capability_fit": b.get("capability_fit", 0),
        "role_transferability": b.get("role_transferability", 0),
        "environment_fit": b.get("environment_fit", 0),
        "gap_cost": b.get("gap_cost", 0),
        "strongest_match": sm.get("title", ""),
        "strongest_evidence": sm.get("portfolio_cv_connection", ""),
        "main_gap": result.get("main_gap", ""),
        "summary_ko": result.get("summary_ko", ""),
        "full": result,
    }


def load_history() -> list:
    if not HISTORY_JSONL.exists():
        return []
    rows = []
    for line in HISTORY_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def save_history(result: dict) -> dict:
    HISTORY_DIR.mkdir(exist_ok=True)
    row = _slim(result)
    # 같은 URL을 다시 분석하면 최신 결과로 교체
    rows = [r for r in load_history() if not (row["url"] and r.get("url") == row["url"])]
    rows.append(row)
    HISTORY_JSONL.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    write_csv(rows)
    HISTORY_HTML.write_text(render_history_html(rows), encoding="utf-8")
    return row


CSV_COLS = ["analyzed_at", "company", "position", "score", "grade", "action",
            "capability_fit", "role_transferability", "environment_fit", "gap_cost",
            "strongest_match", "main_gap", "url"]


def write_csv(rows: list):
    # utf-8-sig: 엑셀/넘버스에서 한글 안 깨지게
    with HISTORY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def render_history_html(rows: list) -> str:
    esc = html.escape
    rows = sorted(rows, key=lambda r: r.get("score") or 0, reverse=True)

    def bar(v, mx):
        pct = max(0, min(100, (v or 0) / mx * 100))
        return f'<div class="mini"><i style="width:{pct:.0f}%"></i></div><span class="n">{v or 0}/{mx}</span>'

    trs = []
    for r in rows:
        g = (r.get("grade") or "").upper()
        full = json.dumps(r.get("full", {}), ensure_ascii=False, indent=2)
        url = r.get("url", "")
        trs.append(f"""
<tr data-grade="{esc(g)}">
  <td class="date">{esc((r.get('analyzed_at') or '')[:10])}</td>
  <td><div class="co">{esc(r.get('company',''))}</div>
      <div class="pos">{esc(r.get('position',''))}</div>
      {f'<a href="{esc(url)}" target="_blank" rel="noopener">공고 열기 ↗</a>' if url else ''}</td>
  <td class="score"><div class="big">{r.get('score',0)}</div>
      <div class="scorebar"><i style="width:{max(0,min(100,r.get('score') or 0))}%"></i></div></td>
  <td><span class="g g-{esc(g)}">{esc(g or '—')}</span><div class="act">{esc(r.get('action',''))}</div></td>
  <td class="bd">
    <div><em>Capability</em>{bar(r.get('capability_fit'),40)}</div>
    <div><em>Transfer</em>{bar(r.get('role_transferability'),25)}</div>
    <div><em>Environment</em>{bar(r.get('environment_fit'),20)}</div>
    <div><em>Gap cost</em>{bar(r.get('gap_cost'),15)}</div>
  </td>
  <td class="txt"><b>{esc(r.get('strongest_match',''))}</b><div>{esc(r.get('strongest_evidence',''))}</div></td>
  <td class="txt">{esc(r.get('main_gap',''))}</td>
</tr>
<tr class="detail"><td colspan="7"><details><summary>전체 분석</summary>
  <p>{esc(r.get('summary_ko',''))}</p><pre>{esc(full)}</pre></details></td></tr>""")

    counts = {k: sum(1 for r in rows if (r.get("grade") or "").upper() == k) for k in ("A", "B", "DISCARD")}
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Job Match 기록</title>
<style>
:root{{--bg:#fafaf8;--fg:#111;--mut:#777;--line:#e4e2dc;--acc:#111;--a:#1f7a4d;--b:#b7791f;--d:#b3261e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141414;--fg:#eee;--mut:#999;--line:#2c2c2c;--acc:#eee}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:13px/1.45 -apple-system,"Apple SD Gothic Neo",sans-serif}}
header{{padding:28px 24px 12px;display:flex;justify-content:space-between;align-items:end;flex-wrap:wrap;gap:12px}}
h1{{margin:0;font-size:12px;letter-spacing:.2em;font-weight:600}} .sub{{color:var(--mut);margin-top:4px}}
.filters button{{border:1px solid var(--line);background:none;color:var(--fg);padding:5px 10px;border-radius:99px;cursor:pointer;font:inherit}}
.filters button.on{{background:var(--acc);color:var(--bg)}}
.wrap{{overflow-x:auto;padding:0 24px 40px}}
table{{border-collapse:collapse;width:100%;min-width:1000px}}
th{{text-align:left;font-size:10px;letter-spacing:.14em;color:var(--mut);font-weight:500;padding:8px 10px;border-bottom:1px solid var(--fg)}}
td{{padding:12px 10px;border-top:1px solid var(--line);vertical-align:top}}
tr.detail td{{border-top:none;padding-top:0}} details summary{{color:var(--mut);cursor:pointer;font-size:11px}}
pre{{white-space:pre-wrap;font-size:11px;background:rgba(127,127,127,.08);padding:10px;max-height:320px;overflow:auto}}
.date{{color:var(--mut);white-space:nowrap}} .co{{font-weight:600}} .pos{{color:var(--mut)}} a{{color:inherit;font-size:11px}}
.big{{font-size:26px;font-weight:600;font-variant-numeric:tabular-nums}}
.scorebar,.mini{{height:4px;background:var(--line);width:90px}} .scorebar i,.mini i{{display:block;height:100%;background:var(--acc)}}
.bd div{{display:flex;align-items:center;gap:6px;margin-bottom:3px}} .bd em{{font-style:normal;width:78px;color:var(--mut);font-size:11px}}
.mini{{width:70px}} .n{{font-size:11px;font-variant-numeric:tabular-nums}}
.g{{display:inline-block;padding:2px 8px;border:1px solid currentColor;font-weight:600;font-size:11px}}
.g-A{{color:var(--a)}} .g-B{{color:var(--b)}} .g-DISCARD{{color:var(--d)}} .act{{margin-top:6px;font-size:11px}}
.txt{{max-width:260px}} .txt div{{color:var(--mut);margin-top:3px}}
</style></head><body>
<header><div><h1>JAY / JOB MATCH HISTORY</h1>
<div class="sub">{len(rows)}건 · A {counts['A']} · B {counts['B']} · DISCARD {counts['DISCARD']} · 점수순 정렬</div></div>
<div class="filters"><button class="on" data-f="">전체</button> <button data-f="A">A</button> <button data-f="B">B</button> <button data-f="DISCARD">DISCARD</button></div></header>
<div class="wrap"><table><thead><tr><th>날짜</th><th>회사 / 포지션</th><th>점수</th><th>등급</th><th>세부 점수</th><th>가장 강한 매치</th><th>주요 갭</th></tr></thead>
<tbody>{''.join(trs) or '<tr><td colspan="7">아직 기록이 없습니다.</td></tr>'}</tbody></table></div>
<script>
document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{{
  document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('on',x===b));
  const f=b.dataset.f;
  document.querySelectorAll('tbody tr[data-grade]').forEach(tr=>{{
    const show=!f||tr.dataset.grade===f; tr.style.display=show?'':'none';
    tr.nextElementSibling.style.display=show?'':'none';}});
}});
</script></body></html>"""


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

        if self.path.startswith("/history"):
            body = render_history_html(load_history()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        self._headers(404)
        self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        if self.path == "/save":
            # 팝업에 남아있던 예전 결과를 기록으로 옮길 때 사용
            try:
                length = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                save_history(data)
                self._headers(200)
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self._headers(500)
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

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
            result["analyzed_at"] = datetime.now().isoformat(timespec="seconds")
            try:
                save_history(result)
                result["saved_to"] = str(HISTORY_HTML)
            except Exception as e:
                print("[Jay Job Matcher] history save failed:", e)

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
    print(f"History chart: http://127.0.0.1:8765/history  (file: {HISTORY_HTML})")
    if not API_KEY:
        print("")
        print("WARNING: ANTHROPIC_API_KEY is not set.")
        print("Set it first:")
        print("  export ANTHROPIC_API_KEY='your_api_key'")
        print("")
    HTTPServer((HOST, PORT), Handler).serve_forever()
