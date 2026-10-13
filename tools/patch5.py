# -*- coding: utf-8 -*-
import sys, io
path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"expected {count}, found {n}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- siteName 한글화 / 표기 정리 ----
for a, b in [
    ('siteName:"PMQ 元創方"', 'siteName:"PMQ 공식"'),
    ('siteName:"블루하우스(香港故事館)"', 'siteName:"블루하우스 공식"'),
    ('siteName:"동화삼원(東華三院) 유마테이 천후묘"', 'siteName:"동화삼원 틴하우 사원"'),
    ('siteName:"시티버스(城巴)"', 'siteName:"시티버스 6번"'),
    ('siteName:"赤柱廣場(링크 REIT)"', 'siteName:"스탠리 플라자"'),
    ('siteName:"포린사(寶蓮禪寺)"', 'siteName:"포린사 공식"'),
    ('6번 버스 중환 출발', '6번 버스 센트럴 출발'),
]:
    src = src.replace(a, b)

# ---- 머레이 하우스: 식당 폐점 반영 (INFO 팁 + 세 번째 여정 Day 2) ----
rep('tip:"바다 쪽 테라스 식당에서 점심하면 좋아요. 옆 블레이크 선착장은 사진 포인트예요."',
    'tip:"2024년부터 건물 안 식당은 없어요. 외관과 블레이크 선착장에서 사진을 찍고, 점심은 바로 옆 스탠리 메인 스트리트 해변 식당이나 스탠리 플라자에서 드세요."')
rep('key:{name:"스탠리 머레이 하우스", why:"홍콩섬 남쪽 바닷가 마을이에요. 2층 버스 앞자리에서 해안도로를 달리고, 콜로니얼 건물 테라스에서 바다 보며 점심을 먹어요. 걷는 양이 적어 엄마와 가장 여유로운 날이에요."}',
    'key:{name:"스탠리 바닷가 마을", why:"홍콩섬 남쪽 바닷가 마을이에요. 2층 버스 앞자리에서 해안도로를 달리고, 해변 산책로 식당에서 바다 보며 점심을 먹어요. 걷는 양이 적어 엄마와 가장 여유로운 날이에요."}')
rep('{t:"12:30",n:"머레이 하우스 · 블레이크 선착장",q:"Murray House Stanley",lat:22.2190,lng:114.2110,why:"1840년대 건물을 옮겨 세운 곳이에요. 바다 쪽 테라스에서 점심을 먹어요.",key:true},',
    '{t:"12:30",n:"머레이 하우스 · 블레이크 선착장",q:"Murray House Stanley",lat:22.2190,lng:114.2110,why:"1840년대 건물을 옮겨 세운 콜로니얼 건물이에요. 바다 앞 선착장과 함께 사진 찍기 좋아요.",note:"건물 안 식당은 2024년에 문을 닫았어요. 점심은 바로 옆 메인 스트리트 해변 식당에서 드세요.",key:true},\n  {t:"13:00",n:"스탠리 메인 스트리트 해변 점심",q:"Stanley Main Street waterfront restaurants",lat:22.2180,lng:114.2118,why:"해변 산책로를 따라 테라스 식당이 늘어서 있어요. 바다 보며 천천히 점심을 먹어요."},')

# ---- 심포니 오브 라이트 종료 예정 메모 (여정 A/B/C) ----
rep('{t:"20:00",n:"심포니 오브 라이트 (스타의 거리)",q:"Avenue of Stars Hong Kong",lat:22.2930,lng:114.1747,why:"매일 밤 8시, 홍콩섬 빌딩들이 음악에 맞춰 빛나는 쇼예요.",note:"끝나면 스타페리로 돌아가 숙소까지 걸어서 15분 정도예요.",key:true}',
    '{t:"20:00",n:"심포니 오브 라이트 (스타의 거리)",q:"Avenue of Stars Hong Kong",lat:22.2930,lng:114.1747,why:"매일 밤 8시, 홍콩섬 빌딩들이 음악에 맞춰 빛나는 쇼예요.",note:"2026년 하반기에 종료될 예정이라 출발 전 운영 여부를 확인하세요. 쇼가 없어도 하버 야경 자체가 볼거리예요. 끝나면 스타페리로 돌아가 숙소까지 걸어서 15분 정도예요.",key:true}')
rep('{t:"20:00",n:"심포니 오브 라이트 (스타의 거리)",q:"Avenue of Stars Hong Kong",lat:22.2930,lng:114.1747,why:"매일 밤 8시, 홍콩섬 빌딩들이 음악에 맞춰 빛나는 쇼예요.",note:"끝나면 스타페리로 센트럴로 돌아가 숙소까지 걸어서 15분이에요.",key:true}',
    '{t:"20:00",n:"심포니 오브 라이트 (스타의 거리)",q:"Avenue of Stars Hong Kong",lat:22.2930,lng:114.1747,why:"매일 밤 8시, 홍콩섬 빌딩들이 음악에 맞춰 빛나는 쇼예요.",note:"2026년 하반기에 종료될 예정이라 출발 전 운영 여부를 확인하세요. 끝나면 스타페리로 센트럴로 돌아가 숙소까지 걸어서 15분이에요.",key:true}')

# ---- 준비 팁: 인타운 체크인 항공사 제한, 공항철도 요금 ----
rep('<div class="tip"><h3>인타운 체크인</h3><p>홍콩역에서 짐을 미리 부칠 수 있어요. 이용 항공사가 되는지와 마감 시간을 출발 전에 확인하세요.</p></div>',
    '<div class="tip"><h3>인타운 체크인</h3><p>홍콩역에서 짐을 미리 부칠 수 있지만 캐세이퍼시픽·홍콩항공·콴타스·싱가포르항공 운항편만 돼요. 다른 항공사면 짐은 숙소에 맡기고 마지막 날 동선을 짧게 잡으세요. 공항철도는 편도 HK$130(옥토퍼스 HK$120)이에요.</p></div>')

# ---- 정보 시트: 최근 확인 메모 + 확인 수준 표시 ----
rep("else if(!hotel) html+=`<div><h3>운영 정보</h3><p class=\"note\">영업시간과 요금은 아래 구글 지도 링크에서 확인하세요.</p></div>`;",
    "else if(!hotel) html+=`<div><h3>운영 정보</h3><p class=\"note\">영업시간과 요금은 아래 구글 지도 링크에서 확인하세요.</p></div>`;\n  if(inf.upd) html+=`<div><h3>최근 확인 메모</h3><p class=\"note\">${esc(inf.upd)}</p></div>`;")
rep("const asOf=inf.asOf||INFO_ASOF;",
    "const asOf=inf.asOf||INFO_ASOF; const confTxt=inf.conf==='high'?'공식 자료로 확인':(inf.conf==='medium'?'복수 자료로 확인':'공식 확인 안 됨 · 참고만');")
rep("html+=`<p class=\"fine\">* 정보 기준일 ${esc(asOf)}",
    "html+=`<p class=\"fine\">* 정보 기준일 ${esc(asOf)}${inf.conf?' · '+confTxt:''}")

io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("ok", len(src))
