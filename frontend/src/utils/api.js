const BASE_URL = "";

function stringifyDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") {
        const loc = Array.isArray(item.loc) ? item.loc.join(".") : "field";
        const msg = item.msg || JSON.stringify(item);
        return `${loc}: ${msg}`;
      }
      return String(item);
    }).join(" | ");
  }
  if (detail && typeof detail === "object") {
    if (typeof detail.message === "string") return detail.message;
    return JSON.stringify(detail);
  }
  return "";
}

async function getErrorMessage(res) {
  let payload;
  try {
    payload = await res.json();
  } catch {
    const text = await res.text().catch(() => "");
    return text || `Server error ${res.status}`;
  }

  const detailMsg = stringifyDetail(payload?.detail);
  if (detailMsg) return detailMsg;

  if (typeof payload?.message === "string") return payload.message;
  if (typeof payload?.error === "string") return payload.error;

  return `Server error ${res.status}`;
}

export async function sendChatMessage(question, topK = 5, section = null) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK, section }),
  });
  if (!res.ok) {
    throw new Error(await getErrorMessage(res));
  }
  return res.json();
}

export async function sendLLMMessage(question, history = []) {
  const res = await fetch(`${BASE_URL}/api/chat/llm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
  if (!res.ok) {
    throw new Error(await getErrorMessage(res));
  }
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export function detectLanguage(text) {
  if (!text) return "en";
  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F]/;
  return arabicRegex.test(text) ? "ar" : "en";
}