const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const urlEl = document.getElementById("url");

function show(id){ document.getElementById(id).classList.remove("hidden"); }
function esc(s=""){ return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[m])); }

async function getCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function extractPage(tabId) {
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => ({
      title: document.title,
      url: location.href,
      text: document.body ? document.body.innerText : ""
    })
  });
  return result;
}

async function analyze(payload) {
  const response = await fetch("http://127.0.0.1:8765/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const err = await response.json().catch(()=>({}));
    throw new Error(err.error || "Local analyzer is not running.");
  }
  return response.json();
}

function render(data){
  document.getElementById("role").textContent = [data.company,data.position].filter(Boolean).join(" · ") || "Job Match";
  document.getElementById("gradeBadge").textContent = data.grade || "—";
  document.getElementById("score").textContent = (data.score ?? "—") + "%";
  document.getElementById("action").textContent = data.action || "—";
  show("summaryCard");

  const b = data.score_breakdown || {};
  const metrics = [
    ["Capability", b.capability_fit, 40],
    ["Transferability", b.role_transferability, 25],
    ["Environment", b.environment_fit, 20],
    ["Gap / Cost", b.gap_cost, 15]
  ];
  document.getElementById("breakdown").innerHTML = metrics.map(([n,v,max])=>`
    <div class="metric">
      <div class="metric-head"><span>${esc(n)}</span><span>${v ?? 0}/${max}</span></div>
      <div class="bar"><div class="bar-fill" style="width:${Math.max(0,Math.min(100,((v??0)/max)*100))}%"></div></div>
    </div>`).join("");
  show("breakdownCard");

  const matches = data.top_matches || [];
  document.getElementById("matches").innerHTML = matches.map((m,i)=>`
    <div class="match-item">
      <div class="match-jd">${i+1}. ${esc(m.jd_requirement)}</div>
      <div class="match-cap">→ ${esc(m.matched_capability)}</div>
      <div class="match-ev">↳ ${esc(m.evidence)}</div>
    </div>`).join("");
  show("matchesCard");

  document.getElementById("gap").textContent = data.main_gap || "—";
  show("gapCard");

  const strongest = data.strongest_match || (matches[0] ? {
    title: matches[0].matched_capability,
    evidence: matches[0].evidence
  } : null);
  if (strongest){
    document.getElementById("strongest").textContent = strongest.title || strongest.matched_capability || "";
    document.getElementById("strongestEvidence").textContent = strongest.evidence || strongest.why || "";
    show("strongestCard");
  }

  resultEl.textContent = data.report || JSON.stringify(data,null,2);
  show("rawDetails");
}

(async () => {
  const tab = await getCurrentTab();
  urlEl.textContent = tab?.url || "No active tab";
})();

document.getElementById("analyze").addEventListener("click", async () => {
  try {
    statusEl.textContent = "페이지 읽는 중…";
    resultEl.textContent = "";
    const tab = await getCurrentTab();
    const page = await extractPage(tab.id);

    statusEl.textContent = "프로파일과 매칭 중…";
    const data = await analyze(page);

    statusEl.textContent = "완료";
    render(data);

    await chrome.storage.local.set({
      lastResult: data,
      lastURL: page.url,
      lastAnalyzedAt: new Date().toISOString()
    });
  } catch (err) {
    statusEl.textContent = "오류";
    resultEl.textContent = err.message + "\n\n먼저 로컬 분석 서버(127.0.0.1:8765)를 실행해야 합니다.";
    show("rawDetails");
  }
});
