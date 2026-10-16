# SUZI 프록시 서버 만들기 (10분)

공유용 `index.html`이 아이폰 Safari 등 **claude.ai 밖에서도 SUZI를 쓰려면** Claude API를 대신 불러 주는 작은 서버가 하나 필요합니다.
API 키를 HTML에 넣으면 받는 사람 모두에게 키가 노출되므로, 키는 이 서버에만 두고 HTML은 서버 주소만 알고 있게 합니다.

```
아이폰 Safari (index.html) ──(서버 주소 + 토큰)──▶ suzi-proxy (Cloudflare Worker, 키 보관) ──▶ Anthropic API
```

## 1. Anthropic API 키 발급
1. https://console.anthropic.com 접속 → API Keys → Create Key
2. 결제 수단 등록(사용량 과금). 모녀 여행 한 번에 수십 번 대화해도 보통 1~3달러 수준입니다.

## 2. Cloudflare Worker 만들기 (무료)
1. https://dash.cloudflare.com 가입 → Workers & Pages → Create → Create Worker → 이름 예: `suzi-proxy` → Deploy
2. "Edit code" → 기존 내용을 지우고 이 폴더의 `worker.js` 내용을 붙여넣기 → Deploy
3. Worker → Settings → Variables and Secrets:
   - `ANTHROPIC_API_KEY` = 1번에서 받은 키 (**Secret**으로)
   - `SUZI_TOKEN` = 아무 긴 문자열, 예: `moneyeo-hk-2026-xyz` (**Secret**으로). 이 토큰을 모르는 사람은 서버를 못 씁니다.
   - `ALLOWED_ORIGIN` = `https://minsukwkd-hub.github.io` (**Text**, 이 페이지의 GitHub Pages 주소). GitHub Pages는 공개 사이트라 토큰이 보일 수 있는데, 이 설정을 하면 그 사이트에서 연 페이지의 요청만 받습니다.
4. 주소를 복사해 둡니다. 예: `https://suzi-proxy.<계정>.workers.dev`

(명령줄이 편하면 `npm i -g wrangler` → `wrangler login` → 이 폴더에서 `wrangler deploy` → `wrangler secret put ANTHROPIC_API_KEY`, `wrangler secret put SUZI_TOKEN`)

## 3. index.html에 연결하기 (둘 중 하나)
- **받는 사람이 설정 없이 쓰게 하려면**: `index.html`에서 `const SUZI_DEFAULT={url:"",token:"",...}` 줄을 찾아 url에 Worker 주소, token에 SUZI_TOKEN을 적고 공유합니다.
- **파일은 그대로 두고 기기마다 설정하려면**: 페이지 → SUZI 버튼 → 오른쪽 위 ⚙ → 연결 방식 "외부 서버" → 서버 주소·토큰 입력 → 저장. 그 기기 브라우저에만 저장됩니다.

## 4. 아이폰에서 여는 법
`.html` 파일을 카톡·에어드롭으로 보내면 iOS가 "미리보기"로 열어 지도·SUZI가 동작하지 않을 수 있습니다.
**파일을 어딘가에 올려 두고 주소로 여는 것**이 가장 확실합니다. 예:
- 이 페이지는 이미 GitHub Pages에 있어요: https://minsukwkd-hub.github.io/moneyeo-hongkong/ → Safari에서 열고 공유 버튼 → "홈 화면에 추가"
- 또는 claude.ai 아티팩트로 게시한 링크 (이 경우 SUZI는 보는 사람의 claude.ai 계정으로 동작, 프록시 불필요)

## 비용·안전 메모
- 서버 비용 0원(Cloudflare 무료 한도), API 비용은 사용량만큼 Anthropic에 과금.
- 토큰이 유출되면 다른 사람이 내 키로 호출할 수 있으니, 토큰을 바꾸거나(Secret 수정) Worker를 끄면 즉시 차단됩니다.
- `ALLOWED_MODELS` 변수로 허용 모델을 제한할 수 있습니다(기본: opus-5-5, sonnet-5-5, haiku-5-5).


## 공유 서버 (2026-10-16, M4)
같은 Worker가 여정 공유 코드와 사진을 보관한다.

| 경로 | 역할 | 저장소 |
|---|---|---|
| `POST /share` `{s, ph?, owner?}` | 짧은 코드 발급(8자) | KV `SHARE`, 90일 만료 |
| `GET /s/<code>` | 코드로 페이로드 읽기 | KV |
| `PUT /p/<code>/<id>` (image/jpeg·png·webp, 3MB 이하, 코드당 60개) | 공유 사진 올리기 | R2 `PHOTOS` |
| `GET /p/<code>/<id>` | 사진 내려받기(1년 캐시) | R2, 수명주기 90일 |
| `GET /` | 기능 안내 `{share, photos, ttlDays}` | - |

쓰기(POST/PUT)는 `ALLOWED_ORIGIN`에서만, 읽기(GET)는 누구나(링크를 받은 사람). IP당 제한: 일반 30회/분, 사진 올리기 120회/분.

### R2 켜기 (사진 공유)
R2는 계정에서 한 번 활성화해야 한다(대시보드 → R2 → 결제 수단 등록, 무료 한도 10GB/월).
1. `npx wrangler r2 bucket create tokki-photos`
2. `npx wrangler r2 bucket lifecycle add tokki-photos --expire-days 90`
3. `wrangler.toml`의 `[[r2_buckets]]` 세 줄 주석 해제 → `npx wrangler deploy`
Worker는 바인딩이 없으면 `photos:false`를 돌려주고 페이지는 "사진 포함" 선택지를 숨긴다.
