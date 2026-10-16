// SUZI 프록시 + 공유 서버 — Cloudflare Workers용 (무료 플랜으로 충분)
// 역할
//   1) POST /            토끼 도우미(Claude) 중계. API 키는 이 Worker의 비밀 변수(ANTHROPIC_API_KEY)에만 있다.
//   2) POST /share       여정 공유 페이로드를 짧은 코드로 보관 (KV, 90일)            → {code}
//      GET  /s/<code>    코드로 페이로드 읽기                                     → {s, ph, created}
//   3) PUT  /p/<code>/<id>  공유에 딸린 사진 올리기 (R2, 최대 3MB, 코드당 60장)   → {ok}
//      GET  /p/<code>/<id>  사진 내려받기 (1년 캐시; R2 수명주기 90일로 지워짐)
// 배포 순서는 같은 폴더의 README.md 참고.
//
// 환경변수(Workers → Settings → Variables and Secrets)
//   ANTHROPIC_API_KEY  (Secret, 필수)  console.anthropic.com 에서 발급한 키
//   SUZI_TOKEN         (Secret, 선택)  쓰지 않기로 함(2026-10-14). 설정하면 Bearer 토큰을 요구한다.
//   ALLOWED_MODELS     (Text,  선택)  쉼표 구분. 기본 "claude-opus-5-5,claude-sonnet-5-5,claude-haiku-5-5"
//   ALLOWED_ORIGIN     (Text,  권장)  페이지를 올린 주소의 origin. 설정하면 쓰기 요청(POST/PUT)은 그 사이트에서만 받는다.
// 바인딩(wrangler.toml): SUZI_RL(IP당 30회/분), UP_RL(사진 올리기 IP당 120회/분), SHARE(KV), PHOTOS(R2)

const API = "https://api.anthropic.com/v1/messages";
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, PUT, OPTIONS",
  "access-control-allow-headers": "content-type, authorization, anthropic-version, anthropic-beta",
  "access-control-max-age": "86400",
};
const SHARE_TTL = 90 * 86400;          // 공유 코드 보관 기간(초)
const SHARE_MAX = 64 * 1024;           // 페이로드 최대 크기
const PHOTO_MAX = 3 * 1024 * 1024;     // 사진 한 장 최대
const PHOTOS_PER_SHARE = 60;           // 코드당 사진(원본+썸네일) 최대 개수
const CODE_RE = /^[a-z0-9]{6,10}$/, ID_RE = /^[a-z0-9]{4,20}(_t)?$/;

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    const url = new URL(req.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    // 읽기(GET)는 링크를 받은 누구나 열 수 있어야 하므로 출처 검사 없음
    if (req.method === "GET") {
      let m;
      if ((m = path.match(/^\/s\/([a-z0-9]{6,10})$/))) return getShare(env, m[1]);
      if ((m = path.match(/^\/p\/([a-z0-9]{6,10})\/([a-z0-9_]{4,22})$/))) return getPhoto(env, m[1], m[2]);
      if (path === "/flights") {
        const ip = req.headers.get("cf-connecting-ip") || "unknown";
        if (!(await allow(env.SUZI_RL, ip))) return json({ error: { message: "rate limited" } }, 429);
        return getFlights(url);
      }
      // 기능 안내: 페이지가 공유 코드·사진 올리기를 지원하는지 확인할 때 쓴다
      return json({ ok: true, service: "tokki", share: !!env.SHARE, photos: !!(env.PHOTOS && env.SHARE), ttlDays: SHARE_TTL / 86400 }, 200);
    }
    if (req.method !== "POST" && req.method !== "PUT") return json({ error: { message: "method" } }, 405);

    // 0) 출처(Origin) 확인 (ALLOWED_ORIGIN을 설정했을 때만, 쓰기 요청에만)
    if (env.ALLOWED_ORIGIN) {
      const origin = req.headers.get("origin") || "";
      const ok = env.ALLOWED_ORIGIN.split(",").map(s => s.trim()).includes(origin);
      if (!ok) return json({ error: { message: "origin not allowed" } }, 403);
    }
    // 1) 토큰 확인 (SUZI_TOKEN을 설정했을 때만)
    if (env.SUZI_TOKEN) {
      const auth = req.headers.get("authorization") || "";
      if (auth !== "Bearer " + env.SUZI_TOKEN) return json({ error: { message: "unauthorized" } }, 401);
    }
    const ip = req.headers.get("cf-connecting-ip") || "unknown";

    // 공유: 코드 발급
    if (req.method === "POST" && path === "/share") {
      if (!(await allow(env.SUZI_RL, ip))) return json({ error: { message: "rate limited" } }, 429);
      return postShare(env, req);
    }
    // 공유 사진 올리기
    let m;
    if (req.method === "PUT" && (m = path.match(/^\/p\/([a-z0-9]{6,10})\/([a-z0-9_]{4,22})$/))) {
      if (!(await allow(env.UP_RL || env.SUZI_RL, ip))) return json({ error: { message: "rate limited" } }, 429);
      return putPhoto(env, req, m[1], m[2]);
    }
    if (req.method !== "POST" || path !== "/") return json({ error: { message: "not found" } }, 404);

    // ---- 토끼 중계 ----
    if (!env.ANTHROPIC_API_KEY) return json({ error: { message: "ANTHROPIC_API_KEY not set" } }, 500);
    if (!(await allow(env.SUZI_RL, ip))) return json({ error: { message: "rate limited" } }, 429);

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
  },
};

async function allow(rl, ip) {
  if (!rl) return true;
  try { const { success } = await rl.limit({ key: ip }); return success; } catch { return true; }
}

function newCode() {
  const a = new Uint8Array(8); crypto.getRandomValues(a);
  return Array.from(a, b => (b % 36).toString(36)).join("");
}

async function postShare(env, req) {
  if (!env.SHARE) return json({ error: { message: "share store not configured" } }, 500);
  const raw = await req.text();
  if (raw.length > SHARE_MAX) return json({ error: { message: "share too large" } }, 413);
  let body; try { body = JSON.parse(raw); } catch { return json({ error: { message: "invalid JSON" } }, 400); }
  if (typeof body.s !== "string" || !/^[A-Za-z0-9_-]{8,}$/.test(body.s)) return json({ error: { message: "bad payload" } }, 400);
  let ph = null;
  if (body.ph != null) {
    if (!Array.isArray(body.ph) || body.ph.length > 60) return json({ error: { message: "bad photos" } }, 400);
    ph = body.ph.map(e => Array.isArray(e) && e.length === 3 && Number.isInteger(e[0]) && Number.isInteger(e[1]) && Array.isArray(e[2]) ? [e[0], e[1], e[2].filter(id => typeof id === "string" && ID_RE.test(id)).slice(0, 20)] : null).filter(Boolean);
  }
  let code = newCode(), tries = 0;
  while (await env.SHARE.get(code) && tries++ < 5) code = newCode();
  const rec = { s: body.s, ph, created: Date.now(), owner: typeof body.owner === "string" ? body.owner.slice(0, 20) : undefined, n: 0 };
  await env.SHARE.put(code, JSON.stringify(rec), { expirationTtl: SHARE_TTL });
  return json({ code, expires: Date.now() + SHARE_TTL * 1000 }, 200);
}

async function getShare(env, code) {
  if (!env.SHARE) return json({ error: { message: "share store not configured" } }, 500);
  const v = await env.SHARE.get(code);
  if (!v) return json({ error: { message: "not found or expired" } }, 404);
  return new Response(v, { status: 200, headers: { ...CORS, "content-type": "application/json", "cache-control": "public, max-age=300" } });
}

async function putPhoto(env, req, code, id) {
  if (!env.PHOTOS || !env.SHARE) return json({ error: { message: "photo store not configured" } }, 500);
  if (!CODE_RE.test(code) || !ID_RE.test(id)) return json({ error: { message: "bad id" } }, 400);
  const recRaw = await env.SHARE.get(code);
  if (!recRaw) return json({ error: { message: "unknown share" } }, 404);
  const rec = JSON.parse(recRaw);
  const ct = req.headers.get("content-type") || "";
  if (!/^image\/(jpeg|png|webp)$/.test(ct)) return json({ error: { message: "image only" } }, 415);
  const len = Number(req.headers.get("content-length") || 0);
  if (len > PHOTO_MAX) return json({ error: { message: "photo too large" } }, 413);
  const buf = await req.arrayBuffer();
  if (buf.byteLength > PHOTO_MAX) return json({ error: { message: "photo too large" } }, 413);
  // 코드당 개수 제한 (KV 레코드의 n을 갱신; 동시 업로드로 몇 장 더 올 수 있지만 상한은 R2 비용 방어용)
  if ((rec.n || 0) >= PHOTOS_PER_SHARE) return json({ error: { message: "too many photos" } }, 429);
  await env.PHOTOS.put(`p/${code}/${id}`, buf, { httpMetadata: { contentType: ct, cacheControl: "public, max-age=31536000, immutable" } });
  rec.n = (rec.n || 0) + 1;
  await env.SHARE.put(code, JSON.stringify(rec), { expirationTtl: SHARE_TTL });
  return json({ ok: true, id, n: rec.n }, 200);
}

async function getPhoto(env, code, id) {
  if (!env.PHOTOS) return json({ error: { message: "photo store not configured" } }, 500);
  const obj = await env.PHOTOS.get(`p/${code}/${id}`);
  if (!obj) return json({ error: { message: "not found" } }, 404);
  const h = new Headers(CORS);
  h.set("content-type", obj.httpMetadata?.contentType || "image/jpeg");
  h.set("cache-control", "public, max-age=31536000, immutable");
  h.set("etag", obj.httpEtag || "");
  return new Response(obj.body, { status: 200, headers: h });
}

// 홍콩공항(HKIA) 공개 운항 정보: 과거 90일 ~ 앞으로 14일. 브라우저에서 직접 못 불러서(CORS 없음) 여기서 중계하고 5분 캐시한다.
//   GET /flights?date=YYYY-MM-DD&no=ZE861  → { date, found:[{dir:"arr"|"dep", no, airline, time, status, origin, destination, terminal, gate, hall, baggage}], updated }
async function getFlights(url) {
  const date = url.searchParams.get("date") || "", no = (url.searchParams.get("no") || "").toUpperCase().replace(/\s+/g, "");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return json({ error: { message: "date=YYYY-MM-DD" } }, 400);
  if (!/^[A-Z0-9]{2}\d{1,4}[A-Z]?$/.test(no)) return json({ error: { message: "no=항공사코드+편명 (예: ZE861)" } }, 400);
  const cache = caches.default; const key = new Request(`https://tokki.cache/flights?date=${date}&no=${no}`);
  const hit = await cache.match(key); if (hit) return hit;
  const found = []; let updated = "";
  for (const dir of ["arr", "dep"]) {
    const src = `https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date=${date}&lang=en&cargo=false&arrival=${dir === "arr"}`;
    let data = null;
    try { const r = await fetch(src, { headers: { "User-Agent": "Mozilla/5.0 (tokki-trip)", "Accept": "application/json" } }); if (!r.ok) continue; data = await r.json(); } catch { continue; }
    const day = (Array.isArray(data) ? data : [data]).find(d => d && d.date === date); if (!day) continue;
    updated = day.lastUpdatedTime || updated;
    for (const f of day.list || []) {
      const codes = (f.flight || []).map(x => String(x.no || "").toUpperCase().replace(/\s+/g, ""));
      if (!codes.includes(no)) continue;
      const main = (f.flight || [])[0] || {};
      found.push({ dir, no: String(main.no || no), airline: main.airline || "", codeshares: codes.filter(c => c !== no), time: f.time || "", status: f.status || "", statusCode: f.statusCode || null,
        origin: f.origin || null, destination: f.destination || null, terminal: f.terminal || "", gate: f.gate || "", hall: f.hall || "", baggage: f.baggage || "", aisle: f.aisle || "" });
    }
  }
  const res = json({ date, no, found, updated, src: "Hong Kong International Airport" }, 200);
  res.headers.set("cache-control", "public, max-age=300");
  try { await cache.put(key, res.clone()); } catch {}
  return res;
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), { status, headers: { ...CORS, "content-type": "application/json", "cache-control": "no-store" } });
}
