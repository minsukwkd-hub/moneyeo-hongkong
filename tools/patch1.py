# -*- coding: utf-8 -*-
import sys, io
path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()
orig_len = len(src)

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"expected {count} occurrence(s), found {n}: {old[:70]!r}"
    src = src.replace(old, new)

# ---------- 3) eyebrow 삭제 + hero 문구 ----------
rep('  <div class="eyebrow">Mother &amp; Daughter · HKG · MFM</div>\n', '')
rep('<p>하루에 핵심 장소는 한 곳만. 나머지는 밥 먹고 쉬는 시간이에요. 궁금한 건 오른쪽 아래 SUZI에게 물어보면 일정에 바로 반영돼요.</p>\n  <div class="status" id="status"></div>',
    '<p>하루에 핵심 장소는 한 곳만. 나머지는 밥 먹고 쉬는 시간이에요. 아래에서 여정을 고르거나 "당신의 여정"에서 직접 꾸며 보세요. 궁금한 건 오른쪽 아래 SUZI에게 물어보면 일정에 바로 반영돼요.</p>\n'
    '  <div class="pickwrap"><div class="picker" id="picker" role="group" aria-label="여정 고르기"></div><p class="pickdesc" id="pickdesc"></p></div>\n'
    '  <div class="status" id="status"></div>')

# ---------- 장소 넣기 시트 HTML ----------
rep('<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>',
'''<div class="sheet" id="addsheet" role="dialog" aria-modal="true" aria-labelledby="addTitle" hidden>
 <div class="sheet-in">
  <div class="sh-head">
    <div class="av plus" aria-hidden="true">＋</div>
    <div><h2 id="addTitle">장소 넣기</h2><p>홍콩·마카오 명소를 골라 Day와 시간에 넣어요</p></div>
    <button class="x" id="addClose" type="button" aria-label="닫기">×</button>
  </div>
  <div class="addform">
    <div class="sel" id="selName">아래에서 장소를 고르세요</div>
    <div class="row">
      <label>Day <select id="addDay"></select></label>
      <label>시간 <input type="time" id="addTime" value="10:00"></label>
      <label class="ck"><input type="checkbox" id="addKey"> 오늘의 한 곳</label>
      <button class="send" id="addGo" type="button" disabled>넣기</button>
    </div>
  </div>
  <input class="search" id="search" type="search" placeholder="장소 이름으로 찾기" aria-label="장소 찾기">
  <div class="chips" id="areas"></div>
  <div class="catalog" id="catalog"></div>
 </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>''')

# ---------- CSS ----------
rep('@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.hop i{animation:none}}',
'''/* 여정 고르기 */
.pickwrap{display:grid;gap:6px}
.picker{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.pick{border:1px solid var(--line);background:var(--surface);border-radius:12px;padding:8px 8px;display:grid;gap:1px;cursor:pointer;text-align:left;min-width:0}
.pick .o{font-size:10.5px;letter-spacing:.06em;color:var(--muted)}
.pick .n{font-size:14px;font-weight:700;overflow-wrap:anywhere}
.pick.on{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.pick.on .o{color:rgba(255,255,255,.75)}
.pick:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.pickdesc{margin:0;font-size:13px;color:var(--muted)}
.linkbtn{border:0;background:none;color:var(--accent);font-weight:700;font-size:13px;cursor:pointer;padding:0}
.linkbtn.warn{color:var(--pin)}
/* 당신의 여정 편집 */
.dayact{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.hint{font-size:13px;color:var(--muted)}
.tl li.ed{grid-template-columns:80px 1fr}
.tin{font:inherit;font-family:var(--mono);font-size:13px;border:1px solid var(--line);border-radius:8px;padding:2px 4px;width:100%;background:var(--surface);color:var(--fg)}
.tl .act{display:flex;gap:12px;align-items:center}
.rm{border:0;background:none;color:var(--pin);font-size:12.5px;cursor:pointer;padding:0;font-weight:700}
.sh-head .av.plus{font-size:24px;font-weight:700;color:var(--blush-ink)}
.addform{padding:10px 16px;border-bottom:1px solid var(--line);display:grid;gap:8px;flex:none}
.addform .sel{font-weight:700;font-size:14px}
.addform .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.addform label{font-size:13px;display:flex;align-items:center;gap:6px}
.addform select,.addform input[type=time]{font:inherit;font-size:14px;border:1px solid var(--line);border-radius:10px;padding:6px 8px;background:var(--bg);color:var(--fg)}
.addform .send{padding:7px 14px;border-radius:10px;margin-left:auto}
.search{margin:10px 16px 0;border:1px solid var(--line);border-radius:12px;padding:9px 12px;font:inherit;font-size:16px;background:var(--bg);color:var(--fg)}
.chip.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.catalog{flex:1;overflow-y:auto;padding:4px 16px 16px;display:grid;gap:8px;align-content:start;min-height:0}
.pl{display:grid;gap:2px;text-align:left;border:1px solid var(--line);background:var(--surface);border-radius:12px;padding:10px 12px;cursor:pointer}
.pl.on{border-color:var(--accent);background:#e6f1ec}
.pl b{font-size:14.5px}
.pl .ar{font-size:11px;color:var(--muted);letter-spacing:.06em}
.pl .w{font-size:12.5px;color:var(--muted)}
.stop{margin-left:8px;border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:2px 10px;font-size:12px;cursor:pointer}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.hop i{animation:none}}''')

# ---------- 일정 데이터: DEFAULT → PLAN_A + B + C + U ----------
start = src.index('const DEFAULT = {')
end = src.index('\n]};\n', start) + len('\n]};\n')
plan_a = src[start:end].replace('const DEFAULT = {', 'const PLAN_A = {', 1)

plans_rest = r'''
const PLAN_B = {
 trip:{dates:"11월 말 (미정)", flightIn:"", flightOut:"", macau:"Day 3 (임시)"},
 days:[
 {title:"도착 · 센트럴 올드타운", sub:"약 7천 보 · 숙소에서 걸어서 다니는 날",
  key:{name:"만모사원 · PMQ", why:"숙소에서 걸어서 10분 거리에 홍콩의 옛 모습과 요즘 감성이 같이 있어요. 향 연기 가득한 사원과 디자이너 공방을 한 골목에서 만나요. 첫날 짐 풀고 가볍게 다니기 딱 좋아요."},
  items:[
  {t:"12:00",n:"홍콩국제공항 도착",q:"Hong Kong International Airport",lat:22.3080,lng:113.9185,why:"공항철도 타고 홍콩역까지 약 24분이에요.",note:"홍콩역에서 숙소까지 택시로 5분 정도예요."},
  {t:"13:30",n:"숙소 짐 맡기고 휴식",q:HOTEL.q,lat:HOTEL.lat,lng:HOTEL.lng,why:"체크인 전이면 짐만 맡기고, 근처에서 가볍게 점심 먹어요.",hotel:true},
  {t:"15:30",n:"만모사원",q:"Man Mo Temple Hong Kong",lat:22.2840,lng:114.1503,why:"1847년에 지어진 홍콩섬에서 가장 오래된 사원이에요. 천장에 매달린 나선형 향이 사진에 예쁘게 나와요.",note:"향 연기가 매워요. 가볍게 둘러보고 나와도 충분해요.",key:true},
  {t:"16:15",n:"캣 스트리트 골동품 거리",q:"Upper Lascar Row Cat Street Hong Kong",lat:22.2843,lng:114.1498,why:"옛 도장, 자기, 빈티지 소품이 늘어선 골목이에요. 엄마와 구경하며 천천히 걷기 좋아요."},
  {t:"17:00",n:"PMQ",q:"PMQ Hong Kong",lat:22.2836,lng:114.1518,why:"옛 경찰 기숙사를 디자이너 공방과 카페로 바꾼 곳이에요. 안뜰에서 쉬면서 기념품 보기 좋아요.",key:true},
  {t:"18:30",n:"소호 저녁 (광둥식 또는 모던)",q:"SoHo Hong Kong Staunton Street",lat:22.2825,lng:114.1530,why:"미드레벨 에스컬레이터 양옆으로 식당이 모여 있어요. 숙소까지 걸어서 15분이라 늦게까지 편해요.",note:"미드레벨 에스컬레이터는 오전 10시 이후엔 올라가는 방향만 운행해요. 내려올 땐 계단이나 택시가 편해요."}
 ]},
 {title:"딤섬 · 완차이 · 하버 야경", sub:"약 9천 보 · 점심 후 숙소에서 쉬고 나가기",
  key:{name:"침사추이 하버 야경", why:"완차이의 옛 골목을 보고 스타페리로 바다를 건너면 해 질 무렵 하버에 도착해요. 심포니 오브 라이트까지 보면 홍콩의 밤을 가장 홍콩답게 즐기는 코스예요."},
  items:[
  {t:"10:30",n:"룽킹힌 딤섬 (포시즌스)",q:"Lung King Heen Four Seasons Hong Kong",lat:22.2868,lng:114.1572,why:"숙소에서 걸어서 10분, 하버가 보이는 창가에서 먹는 고급 딤섬이에요. 엄마께 대접하는 느낌으로 좋아요.",note:"예약이 꼭 필요해요. 부담되면 홍콩역 팀호완도 가까워요."},
  {t:"13:00",n:"숙소 휴식",q:HOTEL.q,lat:HOTEL.lat,lng:HOTEL.lng,why:"오후 일정을 위해 체력을 아껴 두는 시간이에요.",hotel:true},
  {t:"15:30",n:"완차이 블루하우스",q:"Blue House Wan Chai",lat:22.2742,lng:114.1750,why:"파란색 옛 아파트와 골목 시장이 남아 있는 동네예요. 관광지 느낌 없이 홍콩 사람들의 일상을 볼 수 있어요.",note:"숙소에서 트램 타고 20분 정도예요. 트램 2층 앞자리에서 보는 거리 풍경도 볼거리예요."},
  {t:"16:30",n:"리퉁 애비뉴",q:"Lee Tung Avenue Hong Kong",lat:22.2756,lng:114.1726,why:"가로수와 등불이 걸린 보행자 거리예요. 카페에서 잠깐 쉬어 가기 좋아요."},
  {t:"17:30",n:"스타페리 (완차이 → 침사추이)",q:"Wan Chai Ferry Pier",lat:22.2820,lng:114.1740,why:"완차이 선착장에서 바로 침사추이로 건너가요. 해 질 무렵 배 위에서 보는 스카이라인이 좋아요."},
  {t:"18:00",n:"K11 뮤제아 · 하버프런트 저녁",q:"K11 MUSEA Hong Kong",lat:22.2945,lng:114.1738,why:"미술관 같은 쇼핑몰이에요. 저녁 먹고 하버 앞 계단에 앉아 야경을 기다려요.",key:true},
  {t:"20:00",n:"심포니 오브 라이트 (스타의 거리)",q:"Avenue of Stars Hong Kong",lat:22.2930,lng:114.1747,why:"매일 밤 8시, 홍콩섬 빌딩들이 음악에 맞춰 빛나는 쇼예요.",note:"끝나면 스타페리로 센트럴로 돌아가 숙소까지 걸어서 15분이에요.",key:true}
 ]},
 {title:"마카오 하루 · 타이파까지", sub:"약 1.1만 보 · 페리 왕복 약 2시간", macau:true,
  key:{name:"마카오 역사지구 · 타이파 빌리지", why:"오전엔 세나도 광장과 성 바울 유적을 보고, 오후엔 파스텔 골목이 예쁜 타이파 빌리지로 옮겨요. 돌아올 땐 타이파 페리터미널이 가까워 동선이 자연스러워요."},
  items:[
  {t:"09:30",n:"마카오 페리 터미널 (신덕센터)",q:"Hong Kong-Macau Ferry Terminal Shun Tak",lat:22.2876,lng:114.1520,why:"숙소에서 걸어서 5분이에요. 터보젯으로 약 1시간 걸려요.",note:"여권 필수예요."},
  {t:"10:45",n:"마카오 외항 페리터미널 도착",q:"Macau Outer Harbour Ferry Terminal",lat:22.1970,lng:113.5590,why:"택시로 세나도 광장까지 10분 정도예요."},
  {t:"11:15",n:"세나도 광장 → 성 도미니크 성당",q:"Senado Square Macau",lat:22.1935,lng:113.5395,why:"물결무늬 돌바닥과 파스텔 건물이 있는 마카오 대표 광장이에요.",key:true},
  {t:"12:15",n:"성 바울 성당 유적",q:"Ruins of St. Paul's Macau",lat:22.1975,lng:113.5409,why:"정면 벽만 남은 마카오의 상징이에요. 계단 아래에서 올려다보며 찍는 사진이 예뻐요.",note:"가는 길 골목에 육포와 과자 가게가 모여 있어요.",key:true},
  {t:"13:15",n:"매캐니즈 점심",q:"Macanese restaurant Macau Peninsula",lat:22.1925,lng:113.5380,why:"포르투갈과 중국 요리가 섞인 마카오만의 음식이에요. 아프리칸 치킨, 미냐가 대표 메뉴예요."},
  {t:"15:00",n:"타이파 빌리지 · 쿤하 거리",q:"Rua do Cunha Taipa Village Macau",lat:22.1535,lng:113.5585,why:"포르투갈풍 파스텔 집들과 골목 간식이 모여 있는 마을이에요. 세나도에서 택시로 15분이에요.",note:"로드 스토우즈 베이커리 에그타르트가 여기 있어요."},
  {t:"16:30",n:"타이파 주택 박물관 산책",q:"Taipa Houses Museum Macau",lat:22.1555,lng:113.5620,why:"민트색 옛 저택 다섯 채가 호수 옆에 나란히 있어요. 사진 찍고 잠깐 쉬어 가기 좋아요."},
  {t:"18:00",n:"타이파 페리터미널 → 홍콩 복귀",q:"Taipa Ferry Terminal Macau",lat:22.1595,lng:113.5790,why:"타이파에서 택시 10분이에요. 셩완행 페리를 타면 숙소 앞에 내려요."}
 ]},
 {title:"빅토리아 피크 · 출국", sub:"약 5천 보 · 짐 먼저 부치고 빈손으로",
  key:{name:"빅토리아 피크 (오전)", why:"맑은 오전에 올라가면 하버와 구룡이 가장 멀리까지 보여요. 피크트램 승강장이 홍콩역에서 가까워 짐을 부친 뒤 빈손으로 다녀오기 좋아요."},
  items:[
  {t:"09:30",n:"체크아웃 → 홍콩역 인타운 체크인",q:"Hong Kong Station Airport Express",lat:22.2849,lng:114.1582,why:"짐을 먼저 부치면 마지막 반나절을 빈손으로 다닐 수 있어요.",note:"이 코스는 오후 4시 이후 출발편일 때 여유로워요. 항공편이 이르면 SUZI에게 \"Day 4를 타이퀀 코스로 바꿔줘\"라고 하세요."},
  {t:"10:15",n:"피크트램 (가든로드 승강장)",q:"Peak Tram Garden Road Lower Terminus",lat:22.2780,lng:114.1590,why:"홍콩역에서 택시로 5분이에요. 오전엔 줄이 짧은 편이에요."},
  {t:"10:45",n:"스카이테라스 428 · 피크 산책",q:"Sky Terrace 428 The Peak",lat:22.2712,lng:114.1497,why:"피크타워 옥상 전망대예요. 걷기 부담 없이 엘리베이터로 올라가 360도로 봐요.",note:"시간이 되면 루가드 로드를 10분만 걸어도 다른 각도의 전망이 나와요.",key:true},
  {t:"12:00",n:"피크에서 가벼운 점심",q:"The Peak Galleria",lat:22.2715,lng:114.1505,why:"여행 마지막 식사를 전망 보며 천천히 해요."},
  {t:"13:00",n:"택시로 홍콩역 → 공항철도",q:"Hong Kong Station Airport Express",lat:22.2849,lng:114.1582,why:"피크에서 홍콩역까지 택시 15분, 공항까지 24분이에요."}
 ]}
]};

const PLAN_C = {
 trip:{dates:"11월 말 (미정)", flightIn:"", flightOut:"", macau:"Day 3 (임시)"},
 days:[
 {title:"도착 · 야우마테이 · 템플 스트리트", sub:"약 7천 보 · 저녁에 야시장 한 곳만",
  key:{name:"템플 스트리트 야시장", why:"해가 지면 붉은 등 아래로 노점과 점집, 길거리 식당이 늘어서는 구룡의 밤이에요. 영화 속 홍콩 분위기를 첫날 저녁에 가볍게 느낄 수 있어요."},
  items:[
  {t:"12:00",n:"홍콩국제공항 도착",q:"Hong Kong International Airport",lat:22.3080,lng:113.9185,why:"공항철도 타고 홍콩역까지 약 24분이에요.",note:"홍콩역에서 숙소까지 택시로 5분 정도예요."},
  {t:"13:30",n:"숙소 짐 맡기고 휴식",q:HOTEL.q,lat:HOTEL.lat,lng:HOTEL.lng,why:"체크인 전이면 짐만 맡기고, 근처에서 가볍게 점심 먹어요.",hotel:true},
  {t:"16:30",n:"틴하우 사원 · 야우마테이 과일시장",q:"Tin Hau Temple Yau Ma Tei",lat:22.3085,lng:114.1700,why:"바다의 여신을 모신 옛 사원이에요. 옆 과일 도매시장은 저녁에 활기가 돌아요.",note:"숙소에서 MTR로 야우마테이역까지 15분 정도예요."},
  {t:"17:30",n:"템플 스트리트 야시장",q:"Temple Street Night Market",lat:22.3075,lng:114.1700,why:"저녁 6시쯤부터 노점이 켜져요. 기념품 구경하고 노천 식당에서 저녁을 먹어요.",note:"가격은 꼭 흥정하세요. 사람 많은 곳이라 가방은 앞으로 메세요.",key:true},
  {t:"19:30",n:"침사추이 하버 야경 (걸어서)",q:"Tsim Sha Tsui Promenade",lat:22.2935,lng:114.1720,why:"야시장에서 걸어서 15분이면 하버예요. 8시 심포니 오브 라이트를 보고 스타페리로 돌아가요."}
 ]},
 {title:"딤섬 · 스탠리 바닷가", sub:"약 8천 보 · 버스 창가에서 바다 보기",
  key:{name:"스탠리 머레이 하우스", why:"홍콩섬 남쪽 바닷가 마을이에요. 2층 버스 앞자리에서 해안도로를 달리고, 콜로니얼 건물 테라스에서 바다 보며 점심을 먹어요. 걷는 양이 적어 엄마와 가장 여유로운 날이에요."},
  items:[
  {t:"10:00",n:"딤섬 브런치 (셩완 동네 딤섬집)",q:"Dim Sum Square Sheung Wan",lat:22.2866,lng:114.1518,why:"숙소 근처 동네 딤섬집이에요. 줄이 짧고 가격이 편해요."},
  {t:"11:30",n:"익스체인지 스퀘어 6번 버스 → 스탠리",q:"Exchange Square Bus Terminus Hong Kong",lat:22.2840,lng:114.1580,why:"2층 앞자리에 앉으면 리펄스베이 해안도로가 창밖으로 펼쳐져요. 40분 정도 걸려요.",note:"옥토퍼스로 탈 수 있어요. 멀미가 있으면 1층이 편해요."},
  {t:"12:30",n:"머레이 하우스 · 블레이크 선착장",q:"Murray House Stanley",lat:22.2190,lng:114.2110,why:"1840년대 건물을 옮겨 세운 곳이에요. 바다 쪽 테라스에서 점심을 먹어요.",key:true},
  {t:"14:00",n:"스탠리 마켓 · 해변 산책",q:"Stanley Market Hong Kong",lat:22.2185,lng:114.2125,why:"작은 시장 골목과 스탠리 메인 비치가 바로 옆이에요. 기념품 보고 바닷가 벤치에서 쉬어요."},
  {t:"16:00",n:"버스로 센트럴 복귀 · 숙소 휴식",q:HOTEL.q,lat:HOTEL.lat,lng:HOTEL.lng,why:"오후에 돌아와 쉬고, 저녁은 숙소 근처에서 가볍게 먹어요.",hotel:true},
  {t:"18:30",n:"셩완 저녁 (완탕면 또는 광둥 가정식)",q:"Sheung Wan Hong Kong",lat:22.2865,lng:114.1500,why:"하루 종일 바람 쐰 뒤라 가까운 곳에서 편하게 먹어요."}
 ]},
 {title:"마카오 하루 · 콜로안까지", sub:"약 1만 보 · 페리 왕복 약 2시간", macau:true,
  key:{name:"콜로안 빌리지", why:"관광객이 적은 마카오 남쪽 어촌 마을이에요. 노란 성당과 바다 앞 광장, 원조 에그타르트 가게가 있어 조용히 쉬어 가기 좋아요."},
  items:[
  {t:"09:30",n:"마카오 페리 터미널 (신덕센터)",q:"Hong Kong-Macau Ferry Terminal Shun Tak",lat:22.2876,lng:114.1520,why:"숙소에서 걸어서 5분이에요. 터보젯으로 약 1시간 걸려요.",note:"여권 필수예요."},
  {t:"10:45",n:"마카오 외항 페리터미널 도착",q:"Macau Outer Harbour Ferry Terminal",lat:22.1970,lng:113.5590,why:"택시로 세나도 광장까지 10분 정도예요."},
  {t:"11:15",n:"세나도 광장 → 성 바울 성당 유적",q:"Senado Square Macau",lat:22.1935,lng:113.5395,why:"마카오의 중심 광장과 상징 유적을 한 번에 돌아요. 언덕을 천천히 올라가요.",key:true},
  {t:"12:30",n:"매캐니즈 점심",q:"Macanese restaurant Macau Peninsula",lat:22.1925,lng:113.5380,why:"포르투갈과 중국 요리가 섞인 마카오만의 음식이에요. 아프리칸 치킨, 미냐가 대표 메뉴예요."},
  {t:"14:30",n:"콜로안 빌리지 · 성 프란시스코 사비에르 성당",q:"St. Francis Xavier Chapel Coloane",lat:22.1210,lng:113.5605,why:"노란색과 흰색의 작은 성당 앞 광장에 타일 벤치가 있어요. 택시로 25분 정도예요.",key:true},
  {t:"15:30",n:"로드 스토우즈 베이커리 (원조)",q:"Lord Stow's Bakery Coloane",lat:22.1218,lng:113.5612,why:"마카오 에그타르트가 처음 시작된 가게예요. 바다 보며 먹어요."},
  {t:"17:00",n:"타이파 페리터미널 → 홍콩 복귀",q:"Taipa Ferry Terminal Macau",lat:22.1595,lng:113.5790,why:"콜로안에서 택시 15분이에요. 셩완행을 타면 숙소 앞에 내려요."}
 ]},
 {title:"란타우 빅부다 · 출국", sub:"약 6천 보 · 공항 옆 섬에서 마무리",
  key:{name:"옹핑 360 · 빅부다", why:"케이블카로 25분 동안 바다와 산 위를 지나면 거대한 청동 불상이 나와요. 퉁청이 공항 바로 옆이라 마지막 날 동선 낭비가 없어요."},
  items:[
  {t:"09:00",n:"체크아웃 → 홍콩역 인타운 체크인",q:"Hong Kong Station Airport Express",lat:22.2849,lng:114.1582,why:"짐을 먼저 부치면 마지막 반나절을 빈손으로 다닐 수 있어요.",note:"오후 4시 이후 출발편일 때 여유로워요. 항공편이 이르면 SUZI에게 Day 4를 타이퀀 코스로 바꿔 달라고 하세요."},
  {t:"10:00",n:"MTR 퉁청선 → 옹핑 360 케이블카",q:"Ngong Ping 360 Tung Chung",lat:22.2895,lng:113.9435,why:"홍콩역에서 퉁청까지 30분, 케이블카 25분이에요.",note:"크리스털 캐빈(바닥 유리)은 선택이에요. 바람이 세면 운행이 멈출 수 있어 당일 운행 여부를 확인하세요."},
  {t:"11:00",n:"빅부다 (천단대불) · 포린사",q:"Tian Tan Buddha",lat:22.2540,lng:113.9050,why:"계단 268개를 오르면 불상 아래에서 란타우 산이 내려다보여요. 힘들면 아래에서 올려다봐도 충분히 커요.",key:true},
  {t:"12:15",n:"포린사 채식 점심",q:"Po Lin Monastery Vegetarian Kitchen",lat:22.2550,lng:113.9055,why:"절에서 운영하는 소박한 채식 식당이에요. 두부와 버섯 요리가 깔끔해요."},
  {t:"13:30",n:"케이블카 하산 → 퉁청 → 공항",q:"Tung Chung Station",lat:22.2893,lng:113.9415,why:"퉁청에서 공항까지 버스 S1으로 10분이에요. 짐은 이미 부쳤으니 출국 심사로 바로 가요."}
 ]}
]};

// 당신의 여정: 도착·출국 뼈대만 두고 나머지는 직접 채워요
const PLAN_U = {
 trip:{dates:"11월 말 (미정)", flightIn:"", flightOut:"", macau:"미정"},
 days:[
 {title:"도착하는 날", items:[
  {t:"12:00",n:"홍콩국제공항 도착",q:"Hong Kong International Airport",lat:22.3080,lng:113.9185,why:"공항철도 타고 홍콩역까지 약 24분이에요.",note:"홍콩역에서 숙소까지 택시로 5분 정도예요."},
  {t:"13:30",n:"숙소 짐 맡기고 휴식",q:HOTEL.q,lat:HOTEL.lat,lng:HOTEL.lng,why:"체크인 전이면 짐만 맡기고, 근처에서 가볍게 점심 먹어요.",hotel:true}
 ]},
 {title:"둘째 날", items:[]},
 {title:"셋째 날", items:[]},
 {title:"떠나는 날", items:[
  {t:"10:00",n:"체크아웃 → 홍콩역 인타운 체크인",q:"Hong Kong Station Airport Express",lat:22.2849,lng:114.1582,why:"짐을 먼저 부치면 마지막 반나절을 빈손으로 다닐 수 있어요.",note:"이용 항공사가 가능한지 미리 확인하세요."},
  {t:"13:30",n:"홍콩역 → 공항철도",q:"Hong Kong Station Airport Express",lat:22.2849,lng:114.1582,why:"공항까지 약 24분이에요. 짐은 이미 부쳤으니 바로 출국 심사로 가요."}
 ]}
]};

const PLANS=[
 {id:"U", ord:"당신의 여정", name:"직접 꾸미기", custom:true, data:PLAN_U,
  desc:"도착과 출국만 정해 두었어요. 각 날의 \"장소 넣기\"로 명소를 골라 Day와 시간에 넣으면 지도와 일정에 바로 반영돼요."},
 {id:"A", ord:"첫 번째 여정", name:"현재 여정", data:PLAN_A,
  desc:"하버 야경 · 빅토리아 피크 · 마카오 역사지구 · 타이퀀. 처음 가는 홍콩의 대표 코스예요."},
 {id:"B", ord:"두 번째 여정", name:"조금 다른 여정", data:PLAN_B,
  desc:"센트럴 올드타운 · 완차이와 하버 야경 · 마카오와 타이파 빌리지 · 오전 피크. 같은 뼈대에 골목 산책을 더했어요."},
 {id:"C", ord:"세 번째 여정", name:"다른 여정", data:PLAN_C,
  desc:"템플 스트리트 야시장 · 스탠리 바닷가 · 마카오 콜로안 · 란타우 빅부다. 시장과 바다, 섬으로 가는 다른 홍콩이에요."}
];

// 장소 넣기 목록: 세 여정의 명소 + 추가 명소
const EXTRA=[
 {n:"레이디스 마켓 (몽콕)",q:"Ladies Market Mong Kok",lat:22.3185,lng:114.1705,why:"옷, 가방, 기념품 노점이 길게 이어진 몽콕의 대표 시장이에요.",note:"흥정은 기본이에요."},
 {n:"꽃 시장 · 금붕어 거리",q:"Flower Market Road Mong Kok",lat:22.3240,lng:114.1710,why:"꽃 가게가 모인 거리와 비닐봉지에 담긴 금붕어가 걸린 거리가 나란히 있어요. 오전 산책에 좋아요."},
 {n:"홍콩 공원 · 플래그스태프 하우스 다기 박물관",q:"Flagstaff House Museum of Tea Ware",lat:22.2775,lng:114.1605,why:"도심 속 조용한 공원과 무료 다기 박물관이에요. 피크트램 승강장 바로 옆이라 묶기 좋아요."},
 {n:"미드레벨 에스컬레이터 · 소호",q:"Central Mid-Levels Escalator",lat:22.2830,lng:114.1545,why:"세계에서 가장 긴 옥외 에스컬레이터예요. 올라가며 양옆 골목 식당을 구경해요.",note:"오전 10시 이후엔 올라가는 방향만 운행해요."},
 {n:"리펄스 베이",q:"Repulse Bay Beach",lat:22.2365,lng:114.1965,why:"홍콩섬 남쪽의 넓은 해변이에요. 모래사장 산책과 해변 카페가 있어요.",note:"스탠리 가는 6번 버스가 지나가요."},
 {n:"마카오 타워",q:"Macau Tower",lat:22.1795,lng:113.5370,why:"338m 타워 전망대예요. 유리 바닥 위에서 마카오 전체를 내려다봐요."},
 {n:"넛츠포드 테라스 (침사추이 저녁)",q:"Knutsford Terrace Hong Kong",lat:22.3000,lng:114.1735,why:"침사추이 골목의 테라스 식당 거리예요. 야경 보기 전 저녁 먹기 좋아요."}
];
const AREAS=["홍콩섬","구룡","홍콩섬 남부","란타우·공항","마카오"];
function areaOf(p){ if(p.lng<113.75) return "마카오"; if(p.lng<114.05) return "란타우·공항"; if(p.lat>=22.29) return "구룡"; if(p.lat<22.245) return "홍콩섬 남부"; return "홍콩섬"; }
const CATALOG=(()=>{
  const skip=new Set(["Hong Kong International Airport","Hong Kong Station Airport Express","Tung Chung Station"]);
  const seen=new Map();
  const push=p=>{ if(!p||p.hotel||!isFinite(p.lat)||skip.has(p.q)) return; const k=p.q||p.n; if(seen.has(k)) return; seen.set(k,{n:p.n,q:p.q||p.n,lat:p.lat,lng:p.lng,why:p.why||"",note:p.note||"",area:areaOf(p)}); };
  [PLAN_A,PLAN_B,PLAN_C].forEach(pl=>pl.days.forEach(d=>d.items.forEach(push))); EXTRA.forEach(push);
  const order=a=>AREAS.indexOf(a);
  return [...seen.values()].sort((a,b)=>order(a.area)-order(b.area));
})();
'''
src = src[:start] + plan_a + plans_rest + src[end:]

# ---------- 상태: 여정별 저장 ----------
rep('''let plan, history=[];
try{ const s=localStorage.getItem(STORE); plan = s?JSON.parse(s):null; }catch(e){ plan=null; }
if(!plan||!Array.isArray(plan.days)) plan = structuredClone(DEFAULT);
function save(){ try{ localStorage.setItem(STORE, JSON.stringify(plan)); }catch(e){} }''',
'''const VKEY="suzi-hk-variant";
const storeKey=id=>"suzi-hk-plan-v2:"+id;
const metaOf=id=>PLANS.find(p=>p.id===id);
let variant=(()=>{ try{ const v=localStorage.getItem(VKEY); return metaOf(v)?v:"A"; }catch(e){ return "A"; } })();
function loadPlan(id){
  let p=null;
  try{ const s=localStorage.getItem(storeKey(id)) || (id==="A"?localStorage.getItem(STORE):null); p=s?JSON.parse(s):null; }catch(e){ p=null; }
  if(!p||!Array.isArray(p.days)) p=structuredClone(metaOf(id).data);
  return p;
}
let plan=loadPlan(variant), history=[];
function currentMeta(){ return metaOf(variant); }
function currentDefault(){ return currentMeta().data; }
function save(){ try{ localStorage.setItem(storeKey(variant), JSON.stringify(plan)); localStorage.setItem(VKEY, variant); }catch(e){} }
function switchPlan(id){ if(!metaOf(id)) return; if(id!==variant){ variant=id; plan=loadPlan(id); history=[]; document.getElementById('undo').disabled=true; } save(); render(); }
function sortDay(d){ d.items.sort((a,b)=>String(a.t).localeCompare(String(b.t))); }
function isMacauPt(p){ return isFinite(p.lng)&&p.lng<113.75; }''')

# ---------- render ----------
r0 = src.index('function render(newIdx){')
r1 = src.index('(function routeMap(){')
new_render = r'''function render(){
  const P=currentMeta(), custom=!!P.custom;
  const t=plan.trip||{};
  let macauDay=t.macau||"미정";
  if(custom){ const mi=plan.days.findIndex(d=>d.items.some(isMacauPt)); macauDay = mi>=0 ? "Day "+(mi+1) : "미정"; }
  const st=[["여행 날짜",t.dates||"미정"],["숙소","셩완 · 3박 고정"],["항공편",[t.flightIn,t.flightOut].filter(Boolean).join(" / ")||"미정"],["마카오 가는 날",macauDay]];
  document.getElementById('status').innerHTML=st.map(([k,v])=>`<div class="stat ${/미정|임시/.test(v)?'todo':''}"><div class="k">${esc(k)}</div><div class="v">${esc(v)}</div></div>`).join('');
  document.getElementById('picker').innerHTML=PLANS.map(p=>`<button type="button" class="pick${p.id===variant?' on':''}" data-id="${p.id}" aria-pressed="${p.id===variant}"><span class="o">${esc(p.ord)}</span><span class="n">${esc(p.name)}</span></button>`).join('');
  document.getElementById('pickdesc').innerHTML=esc(P.desc)+(custom?'':' <button class="linkbtn" type="button" id="copyToMine">이 여정을 바탕으로 직접 꾸미기 →</button>');
  const isMac=d=>d.macau||(custom&&d.items.some(isMacauPt));
  document.getElementById('tabs').innerHTML=`<a href="#overview">전체 지도</a>`+plan.days.map((d,i)=>`<a href="#d${i+1}">Day ${i+1}${isMac(d)?' 마카오':''}</a>`).join('')+`<a href="#tips">준비 팁</a>`;
  const host=document.getElementById('days'); host.innerHTML='';
  plan.days.forEach((d,di)=>{
    const sec=document.createElement('section'); sec.id='d'+(di+1);
    const keyIt=d.items.find(x=>x.key&&!x.hotel);
    const keyCard=custom?(keyIt?{name:keyIt.n,why:keyIt.why}:null):d.key;
    const sub=custom?`${d.items.length}곳 · 오늘의 한 곳 ${keyIt?keyIt.n:'미정'}`:(d.sub||'');
    sec.innerHTML=`<div class="dayhead"><div class="daynum">${String(di+1).padStart(2,'0')}</div><h2>${esc(d.title)}</h2><div class="sub">${esc(sub)}</div></div>`
      +(custom?`<div class="dayact"><button class="ghost addbtn" type="button" data-day="${di+1}">＋ 장소 넣기</button>${d.items.some(x=>!x.hotel)?'':'<span class="hint">아직 비어 있어요. 장소를 골라 넣어 보세요.</span>'}</div>`:'')
      +(isMac(d)?`<div class="callout"><b>날짜 고정 예정</b> 마카오 행사 날짜가 정해지면 SUZI에게 "마카오를 Day ○로 옮겨줘"라고 하세요. 11월 하순 그랑프리 기간엔 도로 통제와 페리 혼잡이 있을 수 있어요.</div>`:'')
      +(keyCard?`<div class="key"><div class="lbl">오늘의 한 곳</div><h3>${esc(keyCard.name)}</h3><p>${esc(keyCard.why||'')}</p></div>`:'')
      +`<div class="mapbox"><div class="map"></div><button class="expand" type="button" data-big="d${di+1}" data-title="Day ${di+1} 지도">크게 보기</button></div><ol class="tl"></ol>`;
    const ol=sec.querySelector('ol');
    d.items.forEach((it,ii)=>{
      it.i=ii+1;
      const li=document.createElement('li');
      li.className=(it.key?'hl ':'')+(it.added?'new ':'')+(custom?'ed':'');
      li.dataset.day=di; li.dataset.idx=ii;
      const tag=it.added?`<span class="tag">${it.by==='me'?'직접 추가':'SUZI 추가'}</span>`:'';
      const tcell=custom?`<div class="t"><input type="time" class="tin" value="${esc(it.t||'')}" aria-label="시간"></div>`:`<div class="t">${esc(it.t||'')}</div>`;
      li.innerHTML=`${tcell}<div class="c"><div class="name"><span class="pn">${ii+1}</span><span>${esc(it.n)}${tag}</span></div><p class="why">${esc(it.why||'')}</p>${it.note?`<p class="note">${esc(it.note)}</p>`:''}<div class="act"><a class="gm" href="${gm(it.q||it.n)}" target="_blank" rel="noopener">구글 지도에서 열기 ↗</a>${custom?'<button class="rm" type="button">빼기</button>':''}</div></div>`;
      ol.appendChild(li);
    });
    host.appendChild(sec);
    let pins=clusterPins(d.items.filter(x=>!x.hotel));
    const hk=pins.length&&pins[0].lng>113.8;
    if(hk) pins.push({...HOTEL,hotel:true,t:"3박 고정",why:"마카오 페리터미널(신덕센터) 바로 옆이에요."});
    const mapEl=sec.querySelector('.map');
    if(pins.length) mount('d'+(di+1),mapEl,{pins}); else sec.querySelector('.mapbox').hidden=true;
  });
  // overview
  const ov=[{n:"홍콩국제공항",q:"Hong Kong International Airport",lat:22.3080,lng:113.9185,i:"✈",why:"공항철도로 홍콩역까지 약 24분"},{...HOTEL,hotel:true,t:"3박 고정",why:"마카오 페리터미널 바로 옆"}];
  plan.days.forEach((d,di)=>{const k=d.items.find(x=>x.key&&!x.hotel&&isFinite(x.lat))||d.items.find(x=>!x.hotel&&isFinite(x.lat)&&x.q!=="Hong Kong International Airport"&&x.q!=="Hong Kong Station Airport Express"); if(k) ov.push({n:`Day ${di+1} · ${k.n}`,q:k.q,lat:k.lat,lng:k.lng,i:di+1,key:true,why:(custom?'':(d.key?d.key.name:''))});});
  mount('ov',document.getElementById('map-overview'),{pins:ov,fit:[[22.09,113.50],[22.36,114.24]],
    lines:[[[22.2885,114.1505],[22.282,114.10],[22.255,114.02],[22.235,113.86],[22.205,113.66],[22.1975,113.5605]],[[22.3080,113.9185],[22.325,113.985],[22.322,114.06],[22.305,114.135],[22.2849,114.1582]]],
    extra:[{lat:22.24,lng:113.78,html:'<span class="lbl sea" style="font-size:11px">마카오 페리 약 1시간</span>'},{lat:22.338,lng:114.02,html:'<span class="lbl sea" style="font-size:11px">공항철도 24분</span>'}]});
}

'''
src = src[:r0] + new_render + src[r1:]

# ---------- reset ----------
rep("document.getElementById('resetYes').onclick=()=>{ snapshot(); plan=structuredClone(DEFAULT);",
    "document.getElementById('resetYes').onclick=()=>{ snapshot(); plan=structuredClone(currentDefault());")

# ---------- 여정 선택 · 장소 넣기 로직 (undo/reset 뒤에 삽입) ----------
rep('// ---- SUZI ----\n',
r'''// ---- 여정 고르기 ----
document.getElementById('picker').onclick=e=>{ const b=e.target.closest('.pick'); if(b) switchPlan(b.dataset.id); };
document.getElementById('pickdesc').addEventListener('click',e=>{
  const b=e.target.closest('#copyToMine'); if(!b) return;
  const cur=loadPlan('U'), filled=cur.days.reduce((n,d)=>n+d.items.filter(x=>!x.hotel).length,0);
  const doCopy=()=>{ const copy=structuredClone(plan); copy.days.forEach(d=>{ delete d.key; delete d.sub; delete d.macau; }); try{ localStorage.setItem(storeKey('U'), JSON.stringify(copy)); }catch(err){} switchPlan('U'); document.getElementById('d1').scrollIntoView({behavior:'smooth',block:'start'}); };
  if(filled<=4){ doCopy(); return; }
  if(b.dataset.arm){ doCopy(); return; }
  b.dataset.arm='1'; b.classList.add('warn'); b.textContent='지금 "당신의 여정"을 덮어쓰게 돼요. 한 번 더 누르면 복사해요';
});

// ---- 당신의 여정: 직접 편집 ----
const addsheet=document.getElementById('addsheet'); let addSel=null, addArea="전체";
function openAdd(day){
  addSel=null; addArea="전체"; addsheet.hidden=false; scrim.hidden=false; fab.hidden=true;
  const ds=document.getElementById('addDay'); ds.innerHTML=plan.days.map((d,i)=>`<option value="${i+1}">Day ${i+1}</option>`).join(''); ds.value=String(day||1);
  document.getElementById('addKey').checked=false; document.getElementById('search').value='';
  renderCatalog(); updateAddForm(); setTimeout(()=>document.getElementById('search').focus(),50);
}
function closeAdd(){ addsheet.hidden=true; scrim.hidden=true; fab.hidden=false; }
function renderCatalog(){
  const qv=document.getElementById('search').value.trim().toLowerCase();
  const list=CATALOG.filter(p=>(addArea==="전체"||p.area===addArea)&&(!qv||p.n.toLowerCase().includes(qv)||p.q.toLowerCase().includes(qv)));
  document.getElementById('areas').innerHTML=["전체",...AREAS].map(a=>`<button class="chip${a===addArea?' on':''}" type="button" data-a="${esc(a)}">${esc(a)}</button>`).join('');
  document.getElementById('catalog').innerHTML=list.length?list.map(p=>`<button class="pl${addSel===p?' on':''}" type="button" data-q="${esc(p.q)}" aria-pressed="${addSel===p}"><b>${esc(p.n)}</b><span class="ar">${esc(p.area)}</span><span class="w">${esc(p.why)}</span></button>`).join(''):'<p class="hint">찾는 장소가 없어요. SUZI에게 "○○ 넣어줘"라고 해 보세요.</p>';
}
function updateAddForm(){ document.getElementById('selName').textContent=addSel?'선택: '+addSel.n:'아래에서 장소를 고르세요'; document.getElementById('addGo').disabled=!addSel; }
document.getElementById('addClose').onclick=closeAdd;
document.getElementById('search').addEventListener('input',renderCatalog);
document.getElementById('areas').onclick=e=>{ const b=e.target.closest('.chip'); if(b){ addArea=b.dataset.a; renderCatalog(); } };
document.getElementById('catalog').onclick=e=>{ const b=e.target.closest('.pl'); if(!b) return; addSel=CATALOG.find(p=>p.q===b.dataset.q)||null; renderCatalog(); updateAddForm(); };
document.getElementById('addGo').onclick=()=>{
  if(!addSel) return;
  const di=dayIdx(document.getElementById('addDay').value), d=plan.days[di];
  const tm=document.getElementById('addTime').value||"10:00";
  snapshot();
  d.items.push({t:tm,n:addSel.n,q:addSel.q,lat:addSel.lat,lng:addSel.lng,why:addSel.why,note:addSel.note,key:document.getElementById('addKey').checked,added:true,by:"me"});
  sortDay(d); save(); render(); closeAdd();
  const sec=document.getElementById('d'+(di+1)); if(sec) sec.scrollIntoView({behavior:'smooth',block:'start'});
};
document.getElementById('days').addEventListener('click',e=>{
  const ab=e.target.closest('.addbtn'); if(ab){ openAdd(+ab.dataset.day); return; }
  const rm=e.target.closest('.rm'); if(rm){ const li=rm.closest('li'); const d=plan.days[+li.dataset.day]; if(!d||!d.items[+li.dataset.idx]) return; snapshot(); d.items.splice(+li.dataset.idx,1); save(); render(); }
});
document.getElementById('days').addEventListener('change',e=>{
  const tin=e.target.closest('.tin'); if(!tin) return;
  const li=tin.closest('li'); const d=plan.days[+li.dataset.day]; const it=d&&d.items[+li.dataset.idx]; if(!it) return;
  snapshot(); it.t=tin.value; sortDay(d); save(); render();
});

// ---- SUZI ----
''')

# scrim / Escape: 두 시트 모두 닫기
rep("fab.onclick=openSheet; document.getElementById('close').onclick=closeSheet; scrim.onclick=closeSheet;",
    "fab.onclick=openSheet; document.getElementById('close').onclick=closeSheet; scrim.onclick=()=>{ if(!sheet.hidden) closeSheet(); if(!addsheet.hidden) closeAdd(); };")
rep("document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&!sheet.hidden) closeSheet(); });",
    "document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ if(!sheet.hidden) closeSheet(); if(!addsheet.hidden) closeAdd(); } });")

# ---------- RULES: 여정 선택 정보 ----------
rep("[현재 일정 JSON]\n${compactPlan()}`;",
    "[여정 선택] 상단에 여정 선택지가 있어: U=당신의 여정(사용자가 직접 꾸미는 일정), A=첫 번째 여정(현재 여정), B=두 번째 여정(조금 다른 여정), C=세 번째 여정(다른 여정). 지금 선택된 여정은 \"${currentMeta().ord} · ${currentMeta().name}\"이야. 사용자가 다른 여정으로 바꿔 달라고 하면 choose_plan 도구를 써. 일정 변경 도구는 항상 지금 선택된 여정에만 적용돼.\n[현재 일정 JSON]\n${compactPlan()}`;")

# ---------- TOOLS: choose_plan ----------
rep(' {name:"set_trip_info",',
    ''' {name:"choose_plan",description:"상단의 여정 선택지를 바꿔. id: U(당신의 여정), A(첫 번째 여정·현재 여정), B(두 번째 여정·조금 다른 여정), C(세 번째 여정·다른 여정). 반환: 선택된 여정 이름.",
  inputSchema:{type:"object",properties:{id:{type:"string",enum:["U","A","B","C"]}},required:["id"]},
  execute(i){ const id=String(i.id||"").toUpperCase(); if(!metaOf(id)) throw new Error("U, A, B, C 중 하나여야 해요"); switchPlan(id); return {selected:metaOf(id).ord+" · "+metaOf(id).name}; }},
 {name:"set_trip_info",''')

# ---------- 모델 상향 + 멈추기 ----------
rep("const out=bubble('ai','<span class=\"hop\"><i></i><i></i><i></i> 깡총깡총 생각 중</span>');",
    "const out=bubble('ai','<span class=\"hop\"><i></i><i></i><i></i> 깊이 생각하는 중이에요 · 1분 정도 걸릴 수 있어요</span><button class=\"stop\" type=\"button\">멈추기</button>');\n  out.querySelector('.stop').onclick=()=>{ if(ctl) ctl.abort(); };")
rep("const opts={signal:ctl.signal,onText:({text})=>{ out.innerHTML=md(text); log.scrollTop=log.scrollHeight; }};",
    "const opts={signal:ctl.signal,modelTier:\"complex\",effort:\"high\",onText:({text})=>{ out.innerHTML=md(text); log.scrollTop=log.scrollHeight; }};")
rep("const {text:ans,truncated}=await sample([{role:\"user\",content:RULES()},...turns],opts);",
    "const res=await sample([{role:\"user\",content:RULES()},...turns],opts); const {text:ans,truncated}=res;\n    if(res.modelTierApplied&&res.modelTierApplied!=='complex'&&!tierNoted){ tierNoted=true; bubble('sys','이 계정에선 기본 모델로 답했어요'); }")
rep("let sample=null, toolsOK=false, busy=false, ctl=null, turns=[];",
    "let sample=null, toolsOK=false, busy=false, ctl=null, turns=[], tierNoted=false;")
rep("if(e&&e.text) out.innerHTML=md(e.text); else out.innerHTML='';",
    "if(e&&e.text) out.innerHTML=md(e.text); else out.remove();")
rep("<p>호텔 · 경로 · 명소 · 항공권 · 요즘 핫한 키워드</p>",
    "<p>호텔 · 경로 · 명소 · 항공권 · 핫 키워드 · 최고 성능 모델로 답해요</p>")

io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("ok", orig_len, "->", len(src))
