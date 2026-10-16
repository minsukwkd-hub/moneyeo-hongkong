# -*- coding: utf-8 -*-
"""장소 사전(data/places-hk.json) 생성기.
1) Overpass(OpenStreetMap)에서 홍콩·마카오 범위의 명소·식당·카페·쇼핑·공원·해변·역·페리·동네를 받는다.
2) OSM의 wikidata 태그로 Wikidata에서 한국어·영어·한자 라벨과 사이트링크 수(인기 지표)를 붙인다.
3) 종류(kind)·인기(pop)를 매겨 압축 배열로 저장한다.
실행: python -I tools/build_places.py [--fetch] [--build]   (원본 JSON은 tools/places_raw/ 에 캐시)
"""
import io, json, os, re, sys, time, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "tools", "places_raw")
OUT = os.path.join(ROOT, "data", "places-hk.json")
UA = "tokki-trip/0.2 (github minsukwkd-hub/moneyeo-hongkong; place index builder)"
BBOX = "22.10,113.45,22.57,114.45"  # 남,서,북,동 (선전 일부 포함 → 나중에 걸러냄)
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"]

CATS = {
    "tourism": 'nwr["tourism"~"^(attraction|museum|viewpoint|artwork|gallery|zoo|theme_park|aquarium|hotel|resort)$"]["name"]',
    "historic": 'nwr["historic"]["name"]',
    "restaurant": 'nwr["amenity"="restaurant"]["name"]',
    "cafe": 'nwr["amenity"~"^(cafe|ice_cream|food_court|bar|pub)$"]["name"]',
    "fastfood": 'nwr["amenity"="fast_food"]["name"]',
    "shop": 'nwr["shop"~"^(mall|department_store)$"]["name"]',
    "market": 'nwr["amenity"="marketplace"]["name"]',
    "park": 'nwr["leisure"~"^(park|garden|nature_reserve|beach_resort)$"]["name"]',
    "nature": 'nwr["natural"~"^(beach|peak)$"]["name"]',
    "station": 'nwr["railway"="station"]["name"]',
    "ferry": 'nwr["amenity"="ferry_terminal"]["name"]',
    "aerial": 'nwr["aerialway"="station"]["name"]',
    "place": 'nwr["place"~"^(suburb|neighbourhood|quarter|town|village)$"]["name"]',
    "temple": 'nwr["amenity"="place_of_worship"]["name"]',
    "bakery": 'nwr["shop"~"^(bakery|confectionery|pastry|tea|coffee|chocolate|ice_cream)$"]["name"]',
    "gift": 'nwr["shop"~"^(gift|souvenir|books|cosmetics)$"]["name"]',
    "casino": 'nwr["amenity"="casino"]["name"]',
}

def http(url, data=None, headers=None, timeout=180):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")

def overpass(q):
    body = urllib.parse.urlencode({"data": "[out:json][timeout:170];%s(%s);out center tags qt;" % (q, BBOX)}).encode()
    last = None
    for attempt in range(6):
        url = OVERPASS[attempt % len(OVERPASS)]
        try:
            txt = http(url, body, {"Content-Type": "application/x-www-form-urlencoded"})
            return json.loads(txt)
        except Exception as e:
            last = e; wait = 8 * (attempt + 1)
            print("  retry", attempt + 1, url.split('/')[2], str(e)[:80], "wait", wait); time.sleep(wait)
    raise last

def fetch():
    os.makedirs(RAW, exist_ok=True)
    for k, q in CATS.items():
        fp = os.path.join(RAW, k + ".json")
        if os.path.exists(fp):
            print(k, "cached"); continue
        print("fetch", k); t = time.time()
        d = overpass(q)
        io.open(fp, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False))
        print("  ", len(d.get("elements", [])), "elements", round(time.time() - t, 1), "s")
        time.sleep(3)

def wikidata_labels(qids):
    """QID 목록 → {qid: {ko,en,zh,sl}} (sl = 사이트링크 수)"""
    fp = os.path.join(RAW, "wd_labels.json")
    cache = json.load(io.open(fp, encoding="utf-8")) if os.path.exists(fp) else {}
    todo = [q for q in qids if q not in cache]
    print("wikidata labels: cached", len(cache), "todo", len(todo))
    # SPARQL은 1분 1회로 제한되므로 wbgetentities(50개씩)로 받는다
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        params = {"action": "wbgetentities", "ids": "|".join(chunk), "props": "labels|sitelinks", "languages": "ko|en|zh-hant|zh", "format": "json"}
        for attempt in range(5):
            try:
                txt = http("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(params), None, {"Accept": "application/json"})
                break
            except Exception as e:
                print("  wd retry", attempt, str(e)[:80]); time.sleep(5 * (attempt + 1))
        else:
            raise RuntimeError("wikidata failed")
        ents = json.loads(txt).get("entities", {})
        for q in chunk:
            e = ents.get(q) or {}
            lb = e.get("labels") or {}
            cache[q] = {"ko": (lb.get("ko") or {}).get("value", ""), "en": (lb.get("en") or {}).get("value", ""),
                        "zh": (lb.get("zh-hant") or lb.get("zh") or {}).get("value", ""), "sl": len(e.get("sitelinks") or {})}
        io.open(fp, "w", encoding="utf-8").write(json.dumps(cache, ensure_ascii=False))
        print("  ", i + len(chunk), "/", len(todo)); time.sleep(0.4)
    return cache

ASCII = re.compile(r"^[\x20-\x7e]+$")
CJK = re.compile(r"[一-鿿]")
HANGUL = re.compile(r"[가-힣]")

KIND_PRI = {"페리": 9, "교통": 8, "명소": 7, "호텔": 6, "전망": 5, "쇼핑": 4, "카페": 3, "식당": 2, "동네": 1}

def kind_of(cat, t):
    tour = t.get("tourism", ""); am = t.get("amenity", "")
    if cat == "ferry" or am == "ferry_terminal": return "페리"
    if cat == "station" or cat == "aerial": return "교통"
    if tour in ("attraction", "museum", "gallery", "zoo", "theme_park", "aquarium", "artwork") or cat in ("historic", "temple", "park"): return "명소"
    if tour in ("hotel", "resort"): return "호텔"
    if tour == "viewpoint" or "peak" in t.get("natural", ""): return "전망"
    if cat == "bakery": return "카페"
    if cat in ("shop", "market", "gift"): return "쇼핑"
    if am in ("cafe", "ice_cream"): return "카페"
    if am in ("restaurant", "fast_food", "food_court", "bar", "pub"): return "식당"
    if cat == "place": return "동네"
    return "명소"

def ai_korean_names(cands):
    """[(key, en, zh)] → {key: ko}. 토끼 프록시(Worker)로 Haiku에게 통용 한국어 표기를 묻는다. 결과는 places_raw/ko_ai.json에 캐시."""
    fp = os.path.join(RAW, "ko_ai.json")
    cache = json.load(io.open(fp, encoding="utf-8")) if os.path.exists(fp) else {}
    todo = [c for c in cands if c[0] not in cache]
    print("ai korean names: cached", len(cache), "todo", len(todo))
    SYS = ("너는 홍콩·마카오 장소 이름을 한국 여행자가 쓰는 한국어 표기로 바꾸는 변환기야. 입력은 [{\"i\":번호,\"en\":영문,\"zh\":한자}] 배열이고, "
           "출력은 같은 번호의 [{\"i\":번호,\"ko\":한국어 표기}] JSON 배열만(설명·코드블록 없이). 규칙: 널리 쓰이는 한국어 명칭이 있으면 그것(Victoria Peak→빅토리아 피크, Tsim Sha Tsui→침사추이, Star Ferry→스타페리, Temple Street→템플 스트리트), "
           "브랜드·체인은 통용 표기(Starbucks→스타벅스, Tsui Wah→추이와), 없으면 영어 발음을 자연스러운 한글로 옮기되 Park/Garden/Museum/Temple/Pier/Station/Market/Beach/Mall 같은 일반 명사는 공원/정원/박물관/사원/부두/역/시장/해변/몰로 번역해 붙여(Kowloon Park→주룽 공원, Sai Ying Pun Market→사이잉푼 시장). "
           "한자만 있고 영문이 없으면 광둥어 통용 표기나 한자 음독 중 한국 여행 안내에 흔한 쪽을 써. 30자 이내.")
    url = "https://suzi-proxy.suzi-proxy.workers.dev/"
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lock = threading.Lock(); done = [0]

    def run_chunk(chunk):
        msg = json.dumps([{"i": k, "en": c[1], "zh": c[2]} for k, c in enumerate(chunk)], ensure_ascii=False)
        body = {"model": "claude-haiku-5-5", "max_tokens": 4000, "stream": False, "system": SYS, "messages": [{"role": "user", "content": msg}], "output_config": {"effort": "low"}}
        txt = None
        for attempt in range(5):
            try:
                txt = http(url, json.dumps(body).encode("utf-8"), {"Content-Type": "application/json", "Origin": "http://localhost:8765", "anthropic-version": "2023-06-01"}, timeout=120)
                break
            except Exception as e:
                print("  ai retry", attempt, str(e)[:100], flush=True); time.sleep(10 * (attempt + 1))
        arr = []
        if txt:
            try:
                r = json.loads(txt); text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
                m = re.search(r"\[[\s\S]*\]", text); arr = json.loads(m.group(0)) if m else []
            except Exception as e:
                print("  parse fail", str(e)[:80], flush=True)
        got = 0
        with lock:
            for o in arr:
                try:
                    k = int(o.get("i")); ko = str(o.get("ko", "")).strip()[:30]
                    if 0 <= k < len(chunk) and ko and HANGUL.search(ko): cache[chunk[k][0]] = ko; got += 1
                except Exception: pass
            if txt:
                for c in chunk: cache.setdefault(c[0], "")
            io.open(fp, "w", encoding="utf-8").write(json.dumps(cache, ensure_ascii=False))
            done[0] += len(chunk); print("  ", done[0], "/", len(todo), "got", got, flush=True)
        time.sleep(1.0)

    chunks = [todo[i:i + 40] for i in range(0, len(todo), 40)]
    with ThreadPoolExecutor(max_workers=4) as ex:  # Worker 제한(IP당 30회/분) 안에서 4개 동시
        list(ex.map(run_chunk, chunks))
    return cache

def review_korean_names(cands):
    """[(key, en, zh, ko_now)] → 더 좋은 모델(Sonnet)로 상위 인기 장소의 AI 표기를 재검토해 ko_ai.json을 덮어쓴다."""
    fp = os.path.join(RAW, "ko_ai.json"); cache = json.load(io.open(fp, encoding="utf-8")) if os.path.exists(fp) else {}
    rfp = os.path.join(RAW, "ko_reviewed.json"); reviewed = json.load(io.open(rfp, encoding="utf-8")) if os.path.exists(rfp) else {}
    todo = [c for c in cands if c[0] not in reviewed]
    print("review korean names: reviewed", len(reviewed), "todo", len(todo))
    SYS = ("너는 홍콩·마카오 여행 가이드북 편집자야. 입력 [{\"i\",\"en\",\"zh\",\"ko\"}]의 ko는 기계가 만든 한국어 표기야. 한국 여행자들이 실제로 쓰는 통용 표기(가이드북·블로그·지도앱 기준)로 고쳐 [{\"i\",\"ko\"}] JSON 배열만 출력해. "
           "이미 맞으면 그대로. 규칙: 유명 명소·역·호텔·체인은 관용 표기(Tsim Sha Tsui→침사추이, Central→센트럴, Sham Shui Po→삼수이포, Wan Chai→완차이, Tai Kwun→타이쿤, PMQ→PMQ, M+→M+, Lan Fong Yuen→란퐁유엔, Tsui Wah→추이와, Kam Wah→캄와). "
           "영어 일반 명사는 번역(Park→공원, Pier→부두, Temple→사원, Market→시장), 고유명사는 광둥어 발음 기준 한글 표기. 30자 이내, 설명 없이 JSON만.")
    url = "https://suzi-proxy.suzi-proxy.workers.dev/"
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lock = threading.Lock(); done = [0]
    def run_chunk(chunk):
        msg = json.dumps([{"i": k, "en": c[1], "zh": c[2], "ko": c[3]} for k, c in enumerate(chunk)], ensure_ascii=False)
        body = {"model": "claude-sonnet-5-5", "max_tokens": 4000, "stream": False, "system": SYS, "messages": [{"role": "user", "content": msg}], "output_config": {"effort": "low"}}
        txt = None
        for attempt in range(5):
            try:
                txt = http(url, json.dumps(body).encode("utf-8"), {"Content-Type": "application/json", "Origin": "http://localhost:8765", "anthropic-version": "2023-06-01"}, timeout=180); break
            except Exception as e:
                print("  review retry", attempt, str(e)[:100], flush=True); time.sleep(10 * (attempt + 1))
        arr = []
        if txt:
            try:
                r = json.loads(txt); text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
                m = re.search(r"\[[\s\S]*\]", text); arr = json.loads(m.group(0)) if m else []
            except Exception as e:
                print("  parse fail", str(e)[:80], flush=True)
        changed = 0
        with lock:
            for o in arr:
                try:
                    k = int(o.get("i")); ko = str(o.get("ko", "")).strip()[:30]
                    if 0 <= k < len(chunk) and ko and HANGUL.search(ko) or (ko and ko.upper() == ko and len(ko) <= 6):
                        if ko != chunk[k][3]: changed += 1
                        cache[chunk[k][0]] = ko; reviewed[chunk[k][0]] = ko
                except Exception: pass
            if txt:
                for c in chunk: reviewed.setdefault(c[0], c[3])
            io.open(fp, "w", encoding="utf-8").write(json.dumps(cache, ensure_ascii=False))
            io.open(rfp, "w", encoding="utf-8").write(json.dumps(reviewed, ensure_ascii=False))
            done[0] += len(chunk); print("  ", done[0], "/", len(todo), "changed", changed, flush=True)
        time.sleep(1.0)
    chunks = [todo[i:i + 40] for i in range(0, len(todo), 40)]
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(run_chunk, chunks))
    return cache

def pick_names(t, wd):
    ko = t.get("name:ko") or (wd.get("ko") if wd else "") or ""
    en = t.get("name:en") or (wd.get("en") if wd else "") or ""
    zh = t.get("name:zh-Hant") or t.get("name:zh") or (wd.get("zh") if wd else "") or ""
    name = t.get("name", "")
    if not en and ASCII.match(name): en = name
    if not zh and CJK.search(name): zh = CJK.sub(lambda m: m.group(0), name)
    # "大館 Tai Kwun" 처럼 섞인 이름 분리
    if name and not ASCII.match(name) and CJK.search(name) and not en:
        m = re.match(r"^([^\x20-\x7e]+)\s+([\x20-\x7e]+)$", name)
        if m: zh = zh or m.group(1); en = m.group(2)
    if not zh and CJK.search(name): zh = name
    return ko.strip(), en.strip(), zh.strip()

def build():
    items = {}  # key → item
    qids = set()
    raw = {}
    for k in CATS:
        fp = os.path.join(RAW, k + ".json")
        if not os.path.exists(fp): print("missing", k); continue
        raw[k] = json.load(io.open(fp, encoding="utf-8")).get("elements", [])
        for e in raw[k]:
            q = (e.get("tags") or {}).get("wikidata", "")
            if re.match(r"^Q\d+$", q): qids.add(q)
    wd = wikidata_labels(sorted(qids))
    for cat, els in raw.items():
        for e in els:
            t = e.get("tags") or {}
            lat = e.get("lat") or (e.get("center") or {}).get("lat"); lon = e.get("lon") or (e.get("center") or {}).get("lon")
            if lat is None or lon is None: continue
            lat = float(lat); lon = float(lon)
            if lat > 22.535 or (lat > 22.47 and lon < 114.09): continue  # 선전
            if t.get("tourism") == "hotel" and not (t.get("stars") or t.get("wikidata") or t.get("name:ko")): continue  # 이름만 있는 작은 숙소는 제외
            nm_all = " ".join([t.get("name", ""), t.get("name:en", "")])
            if re.search(r"sitting-out|sitting out|rest garden|playground|boundary stone|sports ground|football pitch|basketball|休憩|遊樂場|球場|界石", nm_all, re.I): continue  # 동네 쉼터·운동장 등 여행과 무관한 곳
            q = t.get("wikidata", ""); w = wd.get(q) if q else None
            ko, en, zh = pick_names(t, w)
            if not (ko or en or zh): continue
            if HANGUL.search(t.get("name", "")) and not ko: ko = t.get("name")
            kind = kind_of(cat, t)
            pop = 0
            if w: pop += 1 + min(2, (w.get("sl") or 0) // 5)
            if ko: pop += 1
            if t.get("tourism") in ("attraction", "museum", "viewpoint", "theme_park", "zoo", "aquarium"): pop += 1
            if cat == "fastfood": pop -= 1
            cuisine = t.get("cuisine", "").replace("_", " ").replace(";", ", ")[:40]
            # 같은 장소 묶기: wikidata id가 같거나, 같은 영문/한자 이름이 100m 안에 있으면 하나로
            key = ("wd:" + q) if q else ((en or zh or ko).lower() + "|" + str(round(lat, 3)) + "," + str(round(lon, 3)))
            it = [ko, en, zh, round(lat, 5), round(lon, 5), kind, pop, cuisine, ""]
            if key in items:
                old = items[key]
                for i in (0, 1, 2, 7):
                    if not old[i] and it[i]: old[i] = it[i]
                old[6] = max(old[6], pop)
                if KIND_PRI.get(kind, 0) > KIND_PRI.get(old[5], 0): old[5] = kind
            else:
                items[key] = it
    out = list(items.values())
    # 한국어 이름이 없는 곳(식당·카페는 알려진 곳만)에 AI 통용 표기를 붙인다
    if "--ko" in sys.argv:
        cands = []
        for x in out:
            if x[0] or not (x[1] or x[2]): continue
            if x[5] in ("식당", "카페") and x[6] < 1: continue
            if x[5] in ("동네", "전망") and x[6] < 1 and not x[1]: continue
            cands.append(((x[1] or "") + "|" + (x[2] or ""), x[1], x[2]))
        seen_keys = {}; uniq = []
        for c in cands:
            if c[0] not in seen_keys: seen_keys[c[0]] = 1; uniq.append(c)
        ai = ai_korean_names(uniq)
        if "--review" in sys.argv:  # 인기 상위(pop>=2)의 AI 표기를 Sonnet으로 재검토
            rc = []; seenr = set()
            for x in out:
                k = (x[1] or "") + "|" + (x[2] or "")
                if not x[0] and x[6] >= 2 and ai.get(k) and k not in seenr: seenr.add(k); rc.append((k, x[1], x[2], ai[k]))
            ai = review_korean_names(rc)
        n = 0
        for x in out:
            if not x[0]:
                ko = ai.get((x[1] or "") + "|" + (x[2] or ""), "")
                if ko: x[0] = ko; x[8] = "ai"; n += 1
        print("ai ko applied", n)
    order = {"명소": 0, "전망": 1, "쇼핑": 2, "호텔": 3, "페리": 4, "교통": 5, "식당": 6, "카페": 7, "동네": 8}
    out.sort(key=lambda x: (-x[6], order.get(x[5], 9), x[0] or x[1] or x[2]))
    doc = {"v": 2, "src": "OpenStreetMap(ODbL) + Wikidata(CC0) + 한국어 표기 일부 AI 추정(kosrc=ai), %s, 홍콩·마카오" % time.strftime("%Y-%m-%d"), "fields": ["ko", "en", "zh", "lat", "lng", "kind", "pop", "cuisine", "kosrc"], "items": out}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    import collections
    kinds = collections.Counter(x[5] for x in out); kos = sum(1 for x in out if x[0])
    print("items", len(out), "with ko", kos, "bytes", os.path.getsize(OUT), dict(kinds))

if __name__ == "__main__":
    args = sys.argv[1:] or ["--fetch", "--build"]
    if "--fetch" in args: fetch()
    if "--build" in args or "--ko" in args: build()
