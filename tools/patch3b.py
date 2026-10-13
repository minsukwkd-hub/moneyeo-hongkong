# -*- coding: utf-8 -*-
import sys, io
path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()
NL = chr(10)

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"expected {count}, found {n}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 기준일 + 사용자/SUZI 수정 오버레이 ----
rep('const KIND={"명소":"명소"',
'''const INFO_ASOF="2026-10-13";
const INFO_STORE="suzi-hk-info-v1";
let INFO_EDIT={}; try{ INFO_EDIT=JSON.parse(localStorage.getItem(INFO_STORE)||"{}")||{}; }catch(e){ INFO_EDIT={}; }
function infoOf(q){ const base=INFO[q]||{}; const ed=INFO_EDIT[q]; return ed?{...base,...ed,edited:true}:base; }
function saveInfoEdit(){ try{ localStorage.setItem(INFO_STORE, JSON.stringify(INFO_EDIT)); }catch(e){} }
function findItemByName(name){
  const s=String(name||"").trim().toLowerCase(); if(!s) return null;
  const all=[]; plan.days.forEach(d=>d.items.forEach(it=>all.push(it))); CATALOG.forEach(p=>all.push(p));
  if(INFO[name]) return {n:name,q:name};
  return all.find(it=>(it.n||"").toLowerCase()===s)||all.find(it=>(it.n||"").toLowerCase().includes(s)||(it.q||"").toLowerCase().includes(s))||null;
}
const KIND={"명소":"명소"''')

# ---- openInfo: infoOf 사용 + 기준일/출처/수정 안내 ----
rep('const inf=INFO[it.q]||{}, kind=kindOf(it), hotel=kind==="호텔";',
    'const inf=infoOf(it.q), kind=kindOf(it), hotel=kind==="호텔";')
rep('html+=`<p class="fine">* 시간·요금은 2025년 기준 참고값이에요. 예약 전에 공식 사이트에서 꼭 확인하세요.</p>`;',
    'const asOf=inf.asOf||INFO_ASOF;' + NL +
    '  html+=`<p class="fine">* 정보 기준일 ${esc(asOf)}${inf.edited?\' · 이 기기에서 직접 고친 값이에요\':\'\'}${inf.src?` · <a href="${esc(inf.src)}" target="_blank" rel="noopener">확인한 출처 ↗</a>`:\'\'}. 현지 사정으로 바뀔 수 있으니 예약 전에 공식 사이트에서 꼭 확인하세요. 달라진 걸 보셨다면 SUZI에게 "${esc(it.n)} 영업시간 ○○로 바꿔줘"라고 하면 바로 고쳐 둘게요.</p>`;')
rep('const inf=INFO[it.q]; if(it.hotel) return "호텔";', 'const inf=infoOf(it.q); if(it.hotel) return "호텔";')

# ---- SUZI 도구: update_info ----
rep(' {name:"set_trip_info",',
    ''' {name:"update_info",description:"장소의 운영 정보(영업시간, 요금, 팁)를 사용자가 알려준 값으로 고쳐. name은 일정이나 목록에 있는 한국어 장소명. 바꿀 필드만 보내. 반환: 고친 장소명.",
  inputSchema:{type:"object",properties:{name:{type:"string"},hours:{type:"string"},fee:{type:"string"},tip:{type:"string"}},required:["name"]},
  execute(i){ const it=findItemByName(i.name); if(!it) throw new Error("그 이름의 장소를 찾지 못했어요"); const q=it.q||it.n; const ed=INFO_EDIT[q]||{};
    if(i.hours) ed.hours=String(i.hours); if(i.fee) ed.fee=String(i.fee); if(i.tip) ed.tip=String(i.tip); ed.asOf=new Date().toISOString().slice(0,10);
    INFO_EDIT[q]=ed; saveInfoEdit(); if(!infosheet.hidden) openInfo(it); return {updated:it.n, fields:Object.keys(ed)}; }},
 {name:"set_trip_info",''')

# ---- RULES: 정보 수정 안내 (템플릿 리터럴 안의 실제 줄바꿈) ----
old = '일정 변경 도구는 항상 지금 선택된 여정에만 적용돼.' + NL + '[현재 일정 JSON]'
new = ('일정 변경 도구는 항상 지금 선택된 여정에만 적용돼.' + NL +
       '[운영 정보] 각 장소의 영업시간·요금은 페이지에 저장된 참고값(기준일 ${INFO_ASOF})이야. 사용자가 "○○ 영업시간/요금/휴무를 △△로 바꿔줘"라고 알려주면 update_info 도구로 고쳐. 네가 아는 값으로 임의로 고치지는 마.' + NL +
       '[현재 일정 JSON]')
rep(old, new)

# ---- 초기화 시 정보 수정도 함께 복원 ----
rep("document.getElementById('resetYes').onclick=()=>{ snapshot(); plan=structuredClone(currentDefault());",
    "document.getElementById('resetYes').onclick=()=>{ snapshot(); INFO_EDIT={}; saveInfoEdit(); plan=structuredClone(currentDefault());")

io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("ok", len(src))
