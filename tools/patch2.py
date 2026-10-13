# -*- coding: utf-8 -*-
import sys, io
path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"expected {count}, found {n}: {old[:70]!r}"
    src = src.replace(old, new)

# ---------- 정보 시트 HTML ----------
rep('<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>',
'''<div class="sheet" id="infosheet" role="dialog" aria-modal="true" aria-labelledby="infoTitle" hidden>
 <div class="sheet-in">
  <div class="sh-head">
    <div class="av kind" id="infoKind" aria-hidden="true"></div>
    <div><h2 id="infoTitle"></h2><p id="infoSub"></p></div>
    <button class="x" id="infoClose" type="button" aria-label="닫기">×</button>
  </div>
  <div class="info" id="infoBody"></div>
 </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>''')

# ---------- CSS ----------
rep('.stop{margin-left:8px;',
'''/* 장소 정보 */
.tl .nm{border:0;background:none;padding:0;text-align:left;font:inherit;font-weight:700;color:inherit;cursor:pointer;display:inline-flex;align-items:center;gap:4px;flex-wrap:wrap}
.tl .nm:after{content:"›";color:var(--muted);font-weight:400;font-size:17px;line-height:1}
.tl .nm:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.sh-head .av.kind{font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--blush-ink);text-align:center;line-height:1.1}
.info{flex:1;overflow-y:auto;padding:12px 16px 20px;display:grid;gap:12px;align-content:start;min-height:0}
.info h3{font-size:12px;letter-spacing:.1em;color:var(--muted);font-weight:700;margin:0 0 4px}
.info p{margin:0;font-size:14px}
.info .note{color:var(--muted);font-size:13px}
.info .kv{display:grid;grid-template-columns:72px 1fr;gap:6px 10px;font-size:13.5px;margin:0}
.info .kv dt{color:var(--muted)}
.info .kv dd{margin:0}
.infomap{height:200px;border-radius:12px;overflow:hidden;border:1px solid var(--line);background:var(--water)}
.info .links{display:flex;gap:10px;flex-wrap:wrap;font-size:13px}
.info .links a{font-weight:700;text-decoration:none}
.info .fine{padding:0;font-size:11.5px}
.info .ask{justify-self:start;border:1px solid var(--accent);background:var(--surface);color:var(--accent);border-radius:999px;padding:7px 14px;font-size:13.5px;font-weight:700;cursor:pointer}
.stop{margin-left:8px;''')

# ---------- 운영 정보 데이터 (CATALOG 정의 뒤에 삽입) ----------
rep("const AREAS=[\"홍콩섬\",\"구룡\",\"홍콩섬 남부\",\"란타우·공항\",\"마카오\"];",
r'''// 장소별 운영 정보 (2025년 기준 참고값 · 예약 전 공식 사이트 확인)
const INFO={
 "Shun Tak Centre Hong Kong":{type:"호텔",hours:"체크인 보통 15:00 · 체크아웃 12:00 (호텔별 상이)",fee:"",tip:"신덕센터(마카오 페리터미널)와 MTR 셩완역이 바로 옆이에요. 홍콩역에서 택시 5분, 트램·스타페리 피어까지 걸어서 10~15분이에요. 호텔 이름이 정해지면 SUZI에게 말해 주세요.",hotel:true},
 "Hong Kong International Airport":{type:"교통",hours:"24시간 운영 · 공항철도 05:50~00:48, 10분 간격",fee:"공항철도 홍콩역까지 편도 HK$115 안팎 (옥토퍼스·QR 할인 있음)",tip:"입국 후 '공항철도(Airport Express)' 표지를 따라가요. 홍콩역에서 숙소까지 택시 5분이에요.",site:"https://www.mtr.com.hk/en/customer/services/complom_free_shuttle_bus.html",siteName:"MTR 공항철도"},
 "Hong Kong Station Airport Express":{type:"교통",hours:"인타운 체크인 05:30~00:30 · 공항철도 05:50~00:48",fee:"공항철도 편도 HK$115 안팎 · 인타운 체크인 무료",tip:"출발 90분~24시간 전에 짐을 부칠 수 있어요(항공사별 상이). 이용 항공사가 인타운 체크인을 지원하는지 꼭 확인하세요.",site:"https://www.mtr.com.hk/en/customer/services/in-town-check-in.html",siteName:"인타운 체크인 안내"},
 "Star Ferry Central Pier 7":{type:"페리",hours:"센트럴 7번 피어 ↔ 침사추이 06:30~23:30, 6~12분 간격",fee:"HK$5~6.5 (평일/주말, 상층 기준) · 옥토퍼스 가능",tip:"상층(upper deck)이 뷰가 좋아요. 해 질 무렵 타면 양쪽 스카이라인을 다 봐요. 10분 걸려요.",site:"https://www.starferry.com.hk",siteName:"스타페리"},
 "Wan Chai Ferry Pier":{type:"페리",hours:"완차이 ↔ 침사추이 07:20~22:50, 8~20분 간격",fee:"HK$5~6.5 · 옥토퍼스 가능",tip:"센트럴 노선보다 한산해요. 완차이 컨벤션센터 옆 선착장에서 타요.",site:"https://www.starferry.com.hk",siteName:"스타페리"},
 "Hong Kong-Macau Ferry Terminal Shun Tak":{type:"페리",hours:"터보젯 셩완 → 마카오 외항 07:00~23:59, 30분 간격(야간 1시간)",fee:"이코노미 평일 HK$175 · 주말 HK$190 · 야간 HK$220 안팎",tip:"여권 필수, 출경 심사가 있어 출발 30분 전엔 도착하세요. 소요 약 55분이에요. 주말·행사 기간엔 온라인 예매를 권해요. 돌아오는 표는 시간 지정 없이도 살 수 있지만 성수기엔 지정이 안전해요.",site:"https://www.turbojet.com.hk",siteName:"터보젯"},
 "Macau Outer Harbour Ferry Terminal":{type:"페리",hours:"터미널 24시간 · 터보젯 마카오 → 셩완 07:00~23:59",fee:"이코노미 HK$175~220 안팎",tip:"택시 승강장이 바로 앞이에요. 세나도 광장까지 10분이에요. 돌아올 땐 출발 30분 전 도착해 출경 심사를 받아요.",site:"https://www.turbojet.com.hk",siteName:"터보젯"},
 "Taipa Ferry Terminal Macau":{type:"페리",hours:"코타이워터젯 타이파 → 셩완 07:00~22:30 안팎 (확인 필요)",fee:"HK$175~200 안팎",tip:"타이파·코타이에서 가까운 터미널이에요. 셩완행과 침사추이(차이나 페리터미널)행이 있으니 '셩완(Sheung Wan)'행을 타세요.",site:"https://www.cotaiwaterjet.com",siteName:"코타이워터젯"},
 "The Peninsula Hong Kong The Lobby":{type:"식당",hours:"애프터눈티 매일 14:00~18:00",fee:"1인 HK$400대 (2인 세트 있음)",tip:"로비 티는 예약을 받지 않아 선착순이에요. 오후 2시 전에 가면 대기가 짧아요. 스마트 캐주얼 복장을 권해요.",site:"https://www.peninsula.com/en/hong-kong",siteName:"페닌슐라 홍콩"},
 "1881 Heritage Hong Kong":{type:"명소",hours:"광장 10:00~22:00 · 상점 11:00~20:00",fee:"무료",tip:"저녁 6시쯤 조명이 켜져요. 시계탑과 함께 찍으면 예뻐요."},
 "Avenue of Stars Hong Kong":{type:"명소",hours:"24시간 · 심포니 오브 라이트 매일 20:00 (약 10분)",fee:"무료",tip:"19:40쯤 자리를 잡으세요. 바람이 있으니 겉옷을 챙기세요."},
 "Tsim Sha Tsui Promenade":{type:"명소",hours:"24시간 · 심포니 오브 라이트 매일 20:00",fee:"무료",tip:"시계탑에서 스타의 거리까지 이어지는 산책로예요. 벤치가 많아 쉬면서 봐요."},
 "Sheung Wan Hong Kong":{type:"명소",hours:"동네 산책 · 가게별 상이",fee:"무료",tip:"할리우드 로드, 캣 스트리트, 건어물 거리(데보로드 웨스트)가 걸어서 10분 안에 있어요."},
 "Maxim's Palace City Hall Hong Kong":{type:"식당",hours:"딤섬 평일 11:00~15:00 · 주말·공휴일 09:00~15:00",fee:"1인 HK$150~250 안팎",tip:"수레 딤섬은 문 여는 시간에 맞춰 가면 대기가 짧아요. 시티홀 2층이에요."},
 "Peak Tram Garden Road Lower Terminus":{type:"교통",hours:"07:30~23:00, 10~15분 간격",fee:"왕복 HK$88 안팎 · 스카이테라스 포함 HK$148 안팎",tip:"오후 4~6시가 가장 붐벼요. 온라인 시간 지정 티켓을 사면 줄이 짧아요. 내려올 땐 택시(약 HK$60)가 편해요.",site:"https://www.thepeak.com.hk",siteName:"더 피크"},
 "Lugard Road Lookout Victoria Peak":{type:"전망",hours:"24시간",fee:"무료",tip:"피크 갤러리아 옆에서 시작하는 평평한 산책로예요. 전망 포인트까지 15~20분, 가로등이 있어 해 진 뒤에도 괜찮아요."},
 "The Peak Tower Hong Kong":{type:"전망",hours:"피크타워 10:00~22:00 · 스카이테라스 428 평일 10:00~22:00, 주말 08:00~22:00",fee:"스카이테라스 단독 HK$75 안팎",tip:"식당은 피크타워·갤러리아에 모여 있어요. 야경 보고 내려오면 택시 줄이 길 수 있어요.",site:"https://www.thepeak.com.hk",siteName:"더 피크"},
 "Sky Terrace 428 The Peak":{type:"전망",hours:"평일 10:00~22:00 · 주말 08:00~22:00",fee:"HK$75 안팎 (피크트램 세트 HK$148 안팎)",tip:"엘리베이터로 올라가는 옥상 전망대라 걷기 부담이 없어요. 오전엔 역광이 덜해 사진이 잘 나와요.",site:"https://www.thepeak.com.hk",siteName:"더 피크"},
 "The Peak Galleria":{type:"식당",hours:"10:00~22:00",fee:"식당별",tip:"옥상 무료 전망대가 있어요. 가벼운 식사는 2~3층 푸드코트가 편해요."},
 "Senado Square Macau":{type:"명소",hours:"광장 24시간 · 성 도미니크 성당 10:00~18:00",fee:"무료",tip:"광장에서 성 바울 유적까지 완만한 오르막 10분이에요. 사람이 많으니 아침 일찍 가면 한산해요."},
 "Ruins of St. Paul's Macau":{type:"명소",hours:"외관 24시간 · 유적 내부·박물관 09:00~18:00",fee:"무료",tip:"계단 아래에서 올려다보며 찍는 사진이 예뻐요. 옆 몬테 요새에 오르면 마카오 전경이 보여요.",site:"https://www.macaotourism.gov.mo",siteName:"마카오 관광청"},
 "Macanese restaurant Macau Peninsula":{type:"식당",hours:"점심 12:00~15:00 (식당별)",fee:"1인 MOP 150~250 안팎",tip:"리토랄(Restaurante Litoral), 아 로르샤(A Lorcha)가 유명해요. 아프리칸 치킨, 포르투갈식 해산물밥, 미냐(다진 고기 볶음)를 시켜 보세요."},
 "Margaret's Cafe e Nata Macau":{type:"카페",hours:"08:30~18:00 · 수요일 휴무 (확인 필요)",fee:"에그타르트 1개 MOP 12 안팎",tip:"세나도 광장에서 걸어서 5분이에요. 점심시간엔 줄이 길어 오전이나 3시 이후가 편해요. 자리가 적어 테이크아웃 후 근처 벤치에서 먹기도 해요."},
 "The Venetian Macao":{type:"명소",hours:"24시간 · 그랜드 캐널 숍 10:00~23:00 · 곤돌라 11:00~22:00",fee:"입장 무료 · 곤돌라 1인 MOP 150 안팎",tip:"실내라 날씨와 상관없이 쉬기 좋아요. 외항·타이파 페리터미널행 무료 셔틀이 있어요.",site:"https://www.venetianmacao.com",siteName:"베네시안 마카오"},
 "Tai Kwun Hong Kong":{type:"명소",hours:"10:00~23:00 · 전시 11:00~19:00",fee:"무료",tip:"미드레벨 에스컬레이터에서 바로 들어가요. 안뜰 카페와 옛 감옥 전시가 있어요.",site:"https://www.taikwun.hk",siteName:"타이퀀"},
 "Man Mo Temple Hong Kong":{type:"명소",hours:"08:00~18:00",fee:"무료 (기부 가능)",tip:"내부 촬영은 가능하지만 조용히 둘러보세요. 바로 옆이 캣 스트리트예요."},
 "Upper Lascar Row Cat Street Hong Kong":{type:"쇼핑",hours:"가게별 10:00~18:00 · 일요일 쉬는 가게 많음",fee:"",tip:"흥정이 가능해요. 작은 자기 잔이나 옛 포스터가 기념품으로 좋아요."},
 "PMQ Hong Kong":{type:"명소",hours:"단지 07:00~23:00 · 상점 11:00~20:00",fee:"무료",tip:"안뜰에 앉을 곳이 많아 쉬어 가기 좋아요. 주말엔 마켓이 열려요.",site:"https://www.pmq.org.hk",siteName:"PMQ"},
 "SoHo Hong Kong Staunton Street":{type:"식당",hours:"식당별 · 저녁 18:00~22:00 중심",fee:"1인 HK$200~400 안팎",tip:"엘긴 스트리트·스턴튼 스트리트 양옆이 식당가예요. 조용한 곳을 원하면 7시 전에 가세요."},
 "Lung King Heen Four Seasons Hong Kong":{type:"식당",hours:"점심 12:00~14:30 (주말 11:30~15:00) · 저녁 18:00~22:30",fee:"딤섬 점심 1인 HK$500~ 안팎",tip:"예약 필수예요. 창가 자리를 요청하면 하버가 보여요. 스마트 캐주얼 복장을 권해요.",site:"https://www.fourseasons.com/hongkong/dining/restaurants/lung_king_heen/",siteName:"룽킹힌"},
 "Blue House Wan Chai":{type:"명소",hours:"외관 자유 · 홍콩 하우스 오브 스토리즈 10:00~18:00 (요일 확인)",fee:"무료",tip:"스톤 눌라 레인 골목 시장과 함께 보세요. 트램 '완차이 시장' 정류장에서 내려요."},
 "Lee Tung Avenue Hong Kong":{type:"쇼핑",hours:"10:00~22:00",fee:"무료",tip:"11월 말엔 크리스마스 장식이 걸려 있어 저녁 사진이 예뻐요."},
 "K11 MUSEA Hong Kong":{type:"쇼핑",hours:"10:00~22:00",fee:"무료",tip:"하버 쪽 야외 계단(Sunken Plaza)에서 야경이 보여요. 식당은 2~5층에 많아요.",site:"https://www.k11musea.com",siteName:"K11 뮤제아"},
 "Rua do Cunha Taipa Village Macau":{type:"명소",hours:"상점 10:00~20:00",fee:"무료",tip:"쿤하 거리 끝 로드 스토우즈 베이커리 타이파점, 포르투갈 식당 안토니오(António)가 가까워요."},
 "Taipa Houses Museum Macau":{type:"명소",hours:"10:00~19:00 · 월요일 휴관",fee:"무료",tip:"민트색 저택 앞 호수길이 사진 포인트예요. 쿤하 거리에서 걸어서 10분이에요."},
 "Tin Hau Temple Yau Ma Tei":{type:"명소",hours:"08:00~17:00",fee:"무료",tip:"사원 앞 공원에서 동네 어르신들이 장기를 둬요. 저녁엔 바로 옆이 야시장이에요."},
 "Temple Street Night Market":{type:"쇼핑",hours:"노점 17:00~23:00 (18시 이후 활기)",fee:"무료",tip:"가격은 흥정하세요. 노천 해산물 식당은 메뉴판 가격을 먼저 확인하세요."},
 "Dim Sum Square Sheung Wan":{type:"식당",hours:"08:00~20:00 안팎",fee:"1인 HK$60~90 안팎",tip:"동네 딤섬집이라 캐주얼해요. 차슈바오, 하가우가 기본이에요."},
 "Exchange Square Bus Terminus Hong Kong":{type:"교통",hours:"6번 버스 06:30~00:00, 10~20분 간격",fee:"HK$10 안팎 · 옥토퍼스 가능",tip:"2층 맨 앞자리에서 리펄스베이 해안도로 뷰가 좋아요. 40~50분 걸려요. 멀미가 있으면 1층이 편해요."},
 "Murray House Stanley":{type:"명소",hours:"건물 24시간 · 식당 11:00~23:00",fee:"무료",tip:"바다 쪽 테라스 식당에서 점심하면 좋아요. 옆 블레이크 선착장은 사진 포인트예요."},
 "Stanley Market Hong Kong":{type:"쇼핑",hours:"10:00~18:00",fee:"무료",tip:"린넨, 실크, 기념품이 많아요. 시장 끝에서 스탠리 메인 비치로 이어져요."},
 "St. Francis Xavier Chapel Coloane":{type:"명소",hours:"10:00~17:00",fee:"무료",tip:"성당 앞 광장 타일 벤치에서 쉬어요. 바다 건너가 중국 헝친이에요."},
 "Lord Stow's Bakery Coloane":{type:"카페",hours:"07:00~22:00",fee:"에그타르트 1개 MOP 12 안팎",tip:"1989년 원조 가게예요. 바로 옆 카페 지점에 앉을 자리가 있어요."},
 "Ngong Ping 360 Tung Chung":{type:"교통",hours:"평일 10:00~18:00 · 주말 09:00~18:30",fee:"왕복 스탠다드 HK$270 안팎 · 크리스털 캐빈 추가 요금",tip:"강풍·점검 시 운행이 멈춰요. 당일 아침 공식 사이트에서 운행 여부와 대기 시간을 확인하세요. 온라인 예매가 줄이 짧아요.",site:"https://www.np360.com.hk",siteName:"옹핑 360"},
 "Tian Tan Buddha":{type:"명소",hours:"10:00~17:30 (불상 아래 전시관) · 외부 자유",fee:"무료 (전시관은 공양권 구매 시)",tip:"계단 268개는 천천히 15분이면 올라요. 힘들면 아래 광장에서 봐도 충분히 커요."},
 "Po Lin Monastery Vegetarian Kitchen":{type:"식당",hours:"11:30~16:30",fee:"세트 1인 HK$120 안팎",tip:"입구 매표소에서 공양권을 먼저 사요. 두부·버섯 요리가 깔끔해요."},
 "Tung Chung Station":{type:"교통",hours:"MTR 06:00~01:00 · 공항행 S1 버스 05:30~00:00",fee:"S1 버스 HK$3.5 안팎",tip:"퉁청역 B출구 버스터미널에서 S1을 타면 공항까지 10분이에요."},
 "Ladies Market Mong Kok":{type:"쇼핑",hours:"12:00~23:30",fee:"무료",tip:"흥정은 처음 부른 값의 절반부터 시작해요."},
 "Flower Market Road Mong Kok":{type:"명소",hours:"09:30~19:30",fee:"무료",tip:"MTR 프린스 에드워드역 B1 출구에서 가까워요. 금붕어 거리는 퉁초이 스트리트예요."},
 "Flagstaff House Museum of Tea Ware":{type:"명소",hours:"10:00~18:00 · 화요일 휴관",fee:"무료",tip:"피크트램 승강장에서 걸어서 5분이에요. 옆 로크차(LockCha) 찻집에서 차와 채식 딤섬을 먹을 수 있어요."},
 "Central Mid-Levels Escalator":{type:"교통",hours:"06:00~10:00 하행 · 10:00~24:00 상행",fee:"무료",tip:"내려올 땐 옆 계단을 이용해요. 중간에 타이퀀·PMQ·소호로 빠질 수 있어요."},
 "Repulse Bay Beach":{type:"명소",hours:"24시간",fee:"무료",tip:"6번 버스로 스탠리 가는 길에 들를 수 있어요. 해변 뒤 '더 펄스' 쇼핑몰에 카페가 있어요."},
 "Macau Tower":{type:"전망",hours:"평일 10:00~21:00 · 주말 09:00~21:00",fee:"전망대 MOP 195 안팎",tip:"58층 유리 바닥이 있어요. 번지점프 구경도 볼거리예요.",site:"https://www.macautower.com.mo",siteName:"마카오 타워"},
 "Knutsford Terrace Hong Kong":{type:"식당",hours:"식당별 · 저녁 18:00~ 늦게까지",fee:"1인 HK$200~350 안팎",tip:"스타의 거리까지 걸어서 15분이에요. 야경 보기 전에 저녁 먹기 좋아요."}
};
const KIND={"명소":"명소","식당":"식당","카페":"카페","호텔":"호텔","페리":"페리","교통":"교통","전망":"전망","쇼핑":"쇼핑"};
function kindOf(it){ const inf=INFO[it.q]; if(it.hotel) return "호텔"; if(inf&&inf.type) return inf.type; const q=(it.q||"")+" "+(it.n||""); if(/ferry|페리/i.test(q)) return "페리"; if(/airport|station|tram|bus|360|escalator|공항|역|트램|버스/i.test(q)) return "교통"; if(/cafe|bakery|카페|에그타르트/i.test(q)) return "카페"; if(/restaurant|dim sum|딤섬|점심|저녁|브런치|티/i.test(q)) return "식당"; return "명소"; }
const AREAS=["홍콩섬","구룡","홍콩섬 남부","란타우·공항","마카오"];''')

# ---------- 타임라인 제목을 버튼으로 ----------
rep("li.innerHTML=`${tcell}<div class=\"c\"><div class=\"name\"><span class=\"pn\">${ii+1}</span><span>${esc(it.n)}${tag}</span></div>",
    "li.innerHTML=`${tcell}<div class=\"c\"><div class=\"name\"><span class=\"pn\">${ii+1}</span><button class=\"nm\" type=\"button\" aria-label=\"${esc(it.n)} 정보 보기\">${esc(it.n)}${tag}</button></div>")

# ---------- 정보 시트 로직 ----------
rep("// ---- SUZI ----\n",
r'''// ---- 장소 정보 시트 ----
const infosheet=document.getElementById('infosheet');
function openInfo(it){
  const inf=INFO[it.q]||{}, kind=kindOf(it), hotel=kind==="호텔";
  document.getElementById('infoKind').textContent=kind;
  document.getElementById('infoTitle').textContent=hotel?"숙소 (셩완)":it.n;
  document.getElementById('infoSub').textContent=[areaOf(it), it.t?('일정 '+it.t):''].filter(Boolean).join(' · ');
  const hoursLabel = kind==="페리"?"운항":(kind==="교통"?"운행":(hotel?"시간":"영업시간"));
  const rows=[[hoursLabel,inf.hours],["요금",inf.fee],["팁",inf.tip]].filter(r=>r[1]);
  let html='';
  html+=`<div><h3>${hotel?"이런 곳이에요":"왜 여기냐면"}</h3><p>${esc(hotel?(inf.tip||it.why||''):(it.why||''))}</p>${(!hotel&&it.note)?`<p class="note">${esc(it.note)}</p>`:''}</div>`;
  const rows2=hotel?rows.filter(r=>r[0]!=="팁"):rows;
  if(rows2.length) html+=`<div><h3>${kind==="페리"?"페리 운항 정보":(kind==="교통"?"운행 정보":(hotel?"숙소 정보":"운영 정보"))}</h3><dl class="kv">${rows2.map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl></div>`;
  else if(!hotel) html+=`<div><h3>운영 정보</h3><p class="note">영업시간과 요금은 아래 구글 지도 링크에서 확인하세요.</p></div>`;
  html+=`<div><h3>위치</h3><div class="infomap" id="infomap"></div></div>`;
  html+=`<div class="links"><a href="${gm(it.q||it.n)}" target="_blank" rel="noopener">구글 지도에서 열기 ↗</a>${inf.site?`<a href="${esc(inf.site)}" target="_blank" rel="noopener">${esc(inf.siteName||'공식 사이트')} ↗</a>`:''}</div>`;
  if(hotel) html+=`<button class="ask" type="button" id="askHotel">SUZI에게 호텔 추천 물어보기</button>`;
  else if(kind==="페리") html+=`<button class="ask" type="button" id="askFerry">SUZI에게 페리 시간표·예매 물어보기</button>`;
  html+=`<p class="fine">* 시간·요금은 2025년 기준 참고값이에요. 예약 전에 공식 사이트에서 꼭 확인하세요.</p>`;
  document.getElementById('infoBody').innerHTML=html;
  infosheet.hidden=false; scrim.hidden=false; fab.hidden=true;
  const el=document.getElementById('infomap');
  if(isFinite(it.lat)&&isFinite(it.lng)){ try{ mount('info',el,{pins:[{...it,i:it.i||1,hotel:hotel}]}); setTimeout(()=>LIVE.info&&LIVE.info.invalidateSize(),60); }catch(e){ el.hidden=true; } }
  else el.hidden=true;
  const ah=document.getElementById('askHotel'); if(ah) ah.onclick=()=>{ closeInfo(); openSheet(); ask(CHIPS[0][1]); };
  const af=document.getElementById('askFerry'); if(af) af.onclick=()=>{ closeInfo(); openSheet(); ask(`${it.n} 페리 운항 시간표, 소요 시간, 예매 방법과 요금을 알려줘. 모녀가 편하게 타는 팁도.`); };
  document.getElementById('infoClose').focus();
}
function closeInfo(){ infosheet.hidden=true; scrim.hidden=true; fab.hidden=false; if(LIVE.info){ LIVE.info.remove(); delete LIVE.info; } }
document.getElementById('infoClose').onclick=closeInfo;
document.getElementById('days').addEventListener('click',e=>{
  const b=e.target.closest('.nm'); if(!b) return;
  const li=b.closest('li'); const d=plan.days[+li.dataset.day]; const it=d&&d.items[+li.dataset.idx]; if(it) openInfo(it);
});

// ---- SUZI ----
''')

rep("scrim.onclick=()=>{ if(!sheet.hidden) closeSheet(); if(!addsheet.hidden) closeAdd(); };",
    "scrim.onclick=()=>{ if(!sheet.hidden) closeSheet(); if(!addsheet.hidden) closeAdd(); if(!infosheet.hidden) closeInfo(); };")
rep("document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ if(!sheet.hidden) closeSheet(); if(!addsheet.hidden) closeAdd(); } });",
    "document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ if(!sheet.hidden) closeSheet(); if(!addsheet.hidden) closeAdd(); if(!infosheet.hidden) closeInfo(); } });")

io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("ok", len(src))
