const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const urlEl = document.getElementById("url");

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
  if (!response.ok) throw new Error("Local analyzer is not running.");
  return response.json();
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
    resultEl.textContent = data.report || JSON.stringify(data, null, 2);

    await chrome.storage.local.set({
      lastResult: data,
      lastURL: page.url,
      lastAnalyzedAt: new Date().toISOString()
    });
  } catch (err) {
    statusEl.textContent = "오류";
    resultEl.textContent =
      err.message +
      "\n\n먼저 로컬 분석 서버(127.0.0.1:8765)를 실행해야 합니다.";
  }
});
