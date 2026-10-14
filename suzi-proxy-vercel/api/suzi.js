// SUZI 프록시 — Vercel Edge Function 버전 (GitHub 계정으로 로그인만 하면 배포 가능, 이메일 인증 불필요)
// 환경변수(Vercel → Project → Settings → Environment Variables)
//   ANTHROPIC_API_KEY (필수)  SUZI_TOKEN (권장)  ALLOWED_ORIGIN (권장, 예 https://minsukwkd-hub.github.io)
//   ALLOWED_MODELS (선택, 기본 "claude-opus-5-5,claude-sonnet-5-5,claude-haiku-5-5")
// regions: Anthropic API는 홍콩(hkg1) 발신을 403으로 막으므로 도쿄에서 실행
export const config = { runtime: "edge", regions: ["hnd1"] };

const API = "https://api.anthropic.com/v1/messages";
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type, authorization, anthropic-version, anthropic-beta",
  "access-control-max-age": "86400",
};
const json = (obj, status) => new Response(JSON.stringify(obj), { status, headers: { ...CORS, "content-type": "application/json" } });

export default async function handler(req) {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
  if (req.method !== "POST") return json({ error: { message: "POST only" } }, 405);
  const env = process.env;

  if (env.ALLOWED_ORIGIN) {
    const origin = req.headers.get("origin") || "";
    if (!env.ALLOWED_ORIGIN.split(",").map(s => s.trim()).includes(origin)) return json({ error: { message: "origin not allowed" } }, 403);
  }
  if (env.SUZI_TOKEN) {
    if ((req.headers.get("authorization") || "") !== "Bearer " + env.SUZI_TOKEN) return json({ error: { message: "unauthorized" } }, 401);
  }
  if (!env.ANTHROPIC_API_KEY) return json({ error: { message: "ANTHROPIC_API_KEY not set" } }, 500);

  let body;
  try { body = await req.json(); } catch { return json({ error: { message: "invalid JSON" } }, 400); }
  const allowed = (env.ALLOWED_MODELS || "claude-opus-5-5,claude-sonnet-5-5,claude-haiku-5-5").split(",").map(s => s.trim());
  if (!allowed.includes(body.model)) return json({ error: { message: "model not allowed: " + body.model } }, 400);
  if (JSON.stringify(body).length > 400_000) return json({ error: { message: "request too large" } }, 413);
  if (!body.max_tokens || body.max_tokens > 16000) body.max_tokens = 8000;

  const headers = {
    "content-type": "application/json",
    "x-api-key": env.ANTHROPIC_API_KEY,
    "anthropic-version": req.headers.get("anthropic-version") || "2023-06-01",
  };
  const beta = req.headers.get("anthropic-beta");
  if (beta) headers["anthropic-beta"] = beta;

  const upstream = await fetch(API, { method: "POST", headers, body: JSON.stringify(body) });
  const out = new Headers(CORS);
  out.set("content-type", upstream.headers.get("content-type") || "application/json");
  out.set("cache-control", "no-store");
  return new Response(upstream.body, { status: upstream.status, headers: out });
}
