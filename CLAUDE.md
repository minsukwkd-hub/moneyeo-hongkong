# 토끼의 여정 (travel-maker)

휴대폰 우선 여행 일정 페이지. 지인 1명과 그 일행이 쓰는 개인 서비스이며, 기능이 완성될 때까지 사용자 범위를 넓히지 않는다. 서비스 이름은 **"토끼의 여정"** 으로 고정(제목·앱명·공유 미리보기 모두).

## 현재 산출물
- `index.html` — 단일 파일 앱(모녀 홍콩·마카오 3박4일). CSS 토큰 → 인라인 Leaflet CSS → 페이지 CSS → 본문 → 시트(SUZI·장소 넣기·장소 정보) → `<script>`.
- 배포: GitHub Pages https://minsukwkd-hub.github.io/moneyeo-hongkong/ (이 저장소 `main` 루트, push 후 1~2분 자동 반영).
- `suzi-proxy/` — Cloudflare Worker 프록시(API 키 보관, Origin·토큰·IP당 10회/분 제한). `wrangler.toml` 포함. `npx wrangler deploy`.
- `suzi-proxy-vercel/` — 같은 프록시의 Vercel Edge Function 버전(대안).
- `deploy.ps1` — GitHub Pages 최초 배포 스크립트(이미 배포됨, 참고용).

## index.html 구조 (수정 시 참고)
- 일정 데이터: `PLAN_A`(현재 여정) `PLAN_B`(조금 다른) `PLAN_C`(다른) `PLAN_U`(당신의 여정 = 직접 꾸미기 뼈대) → `PLANS` 배열. 저장: localStorage `suzi-hk-plan-v2:<id>`, 선택 여정 `suzi-hk-variant`.
- 장소 사전: `CATALOG`(세 여정 + `EXTRA`에서 q 기준 중복 제거, `areaOf`로 지역 분류). 운영 정보: `INFO` (키 = 구글지도 검색어 q; `hours, fee, tip, site, siteName, src, upd, conf`). 기준일 `INFO_ASOF`. 사용자/SUZI 수정 오버레이 `INFO_EDIT` → `suzi-hk-info-v1`.
- 렌더: `render()` 하나가 상단 상태·여정 선택 버튼·탭·Day 섹션·전체 지도를 모두 다시 그린다. 지도는 Leaflet + 내장 해안선 `LANDGEO`(타일 없음) — 좌표는 홍콩·마카오 범위만 의미 있음.
- 시트: SUZI(`#sheet`), 장소 넣기(`#addsheet`, 직접 꾸미기에서만), 장소 정보(`#infosheet`, 제목 클릭).
- SUZI 연결 어댑터(`connect()`): ① claude.ai 아티팩트 `window.claude` sample → ② 외부 서버(`CONN.url`, Bearer 토큰) → ③ API 키 직접(테스트용). 설정은 ⚙, localStorage `suzi-hk-conn-v1`. 공유용 기본값은 `SUZI_DEFAULT` 상수.
- SUZI 직접 호출(`apiChat`): Messages API 스트리밍(SSE) + 수동 tool loop. 모델 기본 `claude-opus-5-5`, `output_config.effort:"high"`, `fallbacks:"default"`(beta 헤더 `server-side-fallback-2026-07-01`). thinking 블록은 서명 포함 그대로 되돌려 보낸다.
- SUZI 도구: add_stop / remove_stop / update_stop / swap_days / choose_plan / update_info / set_trip_info.
- 파일이 크다(≈280KB, LANDGEO 때문). 편집은 정확한 문자열 치환으로 하고, 끝나면 `<script>` 본문을 `new Function`으로 문법 검사한다.

## 작업 규칙
- UI/UX 뼈대(색·폰트·레이아웃·시트 방식)는 사용자가 확정함. 기능은 더하되 모양을 바꾸지 않는다.
- 이 폴더는 독립 git 저장소(GitHub `minsukwkd-hub/moneyeo-hongkong`, 공개). 회사 GitLab·다른 저장소는 절대 건드리지 않는다.
- 공개 저장소이므로 API 키·이메일·계정 ID를 커밋하지 않는다. 비밀은 Worker Secret에만.
- 운영 정보(`INFO`)는 웹 검증 날짜를 `INFO_ASOF`로 표시한다. 값이 바뀌면 `src`·`upd`·`conf`도 함께 갱신.
- 커밋 메시지 끝에 `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- 로컬 확인: `python -m http.server 8765 --directory .` 후 http://localhost:8765/index.html (file:// 로 열면 fetch·일부 기능 제한).

## 진행 상태 (2026-10-14)
- SUZI 서버 연결 **미완**: Cloudflare 계정 이메일 미인증으로 `wrangler deploy` 거부(code 10034). wrangler OAuth 로그인은 완료. 메일 인증이 안 되면 `suzi-proxy-vercel`로 전환(GitHub 로그인만 필요).
- 남은 순서: 배포 → `SUZI_TOKEN` 생성·등록 → 사용자가 터미널에서 `ANTHROPIC_API_KEY` secret 직접 입력(키는 채팅으로 주고받지 않음) → `SUZI_DEFAULT`에 url/token → push → 실제 질문으로 검증.
- Anthropic 콘솔: 크레딧 충전·자동충전 켜짐. 월 한도 설정 권장.

## 로드맵
1. SUZI 연결 완료.
2. "직접 꾸미기 + 여행 짜기"를 실제 운용 수준으로: 여행 기본정보(날짜·항공편·숙소) 입력, 일정 순서 변경, 소요·이동시간 계산, 하루 부하 경고, 목록에 없는 장소 추가, 내보내기·불러오기.
3. 트리플(Triple)식 공유: 내 여정을 링크로 외부 인원에게 보여 주고, 상대가 "내 여정으로 가져오기"로 복사해 편집. 서버 없이 링크에 여정을 압축해 담는 방식부터.
4. 홍콩 전용을 넘어 사용자가 자신의 여정을 계속 기록하는 서비스로 확장(여행 목록 → 여행별 일정 → 장소 사전, 방문 체크·메모·지출·여행 일기).
