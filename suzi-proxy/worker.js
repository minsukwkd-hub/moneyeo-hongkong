// SUZI 프록시 — Cloudflare Workers용 (무료 플랜으로 충분)
// 역할: 공유용 HTML(index.html)이 Anthropic API 키 없이 SUZI를 쓸 수 있게 중계한다.
//       API 키는 이 Worker의 비밀 변수(ANTHROPIC_API_KEY)에만 있고, 받는 사람 휴대폰에는 절대 내려가지 않는다.
// 배포 순서는 같은 폴더의 README.md 참고.
//
// 환경변수(Workers → Settings → Variables and Secrets)
//   ANTHROPIC_API_KEY  (Secret, 필수)  console.anthropic.com 에서 발급한 키
//   SUZI_TOKEN         (Secret, 권장)  아무 긴 문자열. index.html 연결 설정의 "서버 토큰"과 같아야 한다.
//   ALLOWED_MODELS     (Text,  선택)  쉼표 구분. 기본 "claude-opus-5-5,claude-sonnet-5-5,claude-haiku-5-5"

const API = "https://api.anthropic.com/v1/messages";
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type, authorization, anthropic-version, anthropic-beta",
  "access-control-max-age": "86400",
};

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (req.method !== "POST") return json({ error: { message: "POST only" } }, 405);

    // 1) 토큰 확인 (SUZI_TOKEN을 설정했을 때만)
    if (env.SUZI_TOKEN) {
      const auth = req.headers.get("authorization") || "";
      if (auth !== "Bearer " + env.SUZI_TOKEN) return json({ error: { message: "unauthorized" } }, 401);
    }
    if (!env.ANTHROPIC_API_KEY) return json({ error: { message: "ANTHROPIC_API_KEY not set" } }, 500);

    // 2) 요청 본문 검사 (모델 허용 목록, 크기 제한)
    let body;
    try { body = await req.json(); } catch { return json({ error: { message: "invalid JSON" } }, 400); }
    const allowed = (env.ALLOWED_MODELS || "claude-opus-5-5,claude-sonnet-5-5,claude-haiku-5-5").split(",").map(s => s.trim());
    if (!allowed.includes(body.model)) return json({ error: { message: "model not allowed: " + body.model } }, 400);
    if (JSON.stringify(body).length > 400_000) return json({ error: { message: "request too large" } }, 413);
    if (!body.max_tokens || body.max_tokens > 16000) body.max_tokens = 8000;

    // 3) Anthropic API로 그대로 전달 (스트리밍 응답을 그대로 흘려보냄)
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
  },
};

function json(obj, status) {
  return new Response(JSON.stringify(obj), { status, headers: { ...CORS, "content-type": "application/json" } });
}
