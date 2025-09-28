// pages/api/chat.js
export default async function handler(req, res) {
  // --- CORS (incl. preflight) ---
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    return res.status(200).end();
  }

  // Enforce POST
  if (req.method !== "POST") {
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Parse body
  const body = req.body || {};
  const {
    messages,
    model: bodyModel = "gpt-4o",
    temperature: bodyTemp = 1.0,
    max_tokens: bodyMax = 500
  } = body;

  if (!Array.isArray(messages) || messages.length === 0) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.status(400).json({ error: "Missing 'messages' array" });
  }

  // Coerce & clamp
  const model = String(bodyModel || "gpt-4o");
  const temperature = Math.min(Math.max(Number(bodyTemp) || 0, 0), 2); // 0..2
  const max_tokens = Math.min(Math.max(parseInt(bodyMax, 10) || 0, 1), 500); // <=500 cap

  // Optional: upstream timeout
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);

  try {
    const r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      signal: controller.signal,
      body: JSON.stringify({
        model,
        messages,
        temperature,
        max_tokens
      })
    });

    const data = await r.json().catch(() => null);
    clearTimeout(timeout);

    if (!r.ok) {
      const errMsg = data?.error?.message || `OpenAI error ${r.status}`;
      res.setHeader("Access-Control-Allow-Origin", "*");
      return res.status(r.status).json({
        error: errMsg,
        appliedSettings: { model, temperature, max_tokens },
        raw: data
      });
    }

    const reply = data?.choices?.[0]?.message?.content?.trim() ?? "";

    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Cache-Control", "no-store");
    return res.status(200).json({
      reply,
      usage: data?.usage ?? null,
      appliedSettings: { model, temperature, max_tokens },
      raw: data
    });
  } catch (err) {
    clearTimeout(timeout);
    const aborted = err?.name === "AbortError";
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.status(aborted ? 504 : 500).json({
      error: aborted ? "Upstream timeout from OpenAI" : String(err),
      appliedSettings: { model, temperature, max_tokens }
    });
  }
}
