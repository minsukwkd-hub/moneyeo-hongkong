# -*- coding: utf-8 -*-
import sys, io
path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"expected {count}, found {n}: {old[:70]!r}"
    src = src.replace(old, new)

# ---------- SUZI 시트 머리: 설정 톱니 + 연결 상태줄 ----------
rep('''    <div><h2 id="suziTitle">SUZI 무엇이든 물어보세요<sup><a href="#fn" id="fnLink" style="color:inherit;text-decoration:none">*</a></sup></h2><p>호텔 · 경로 · 명소 · 항공권 · 핫 키워드 · 최고 성능 모델로 답해요</p></div>
    <button class="x" id="close" type="button" aria-label="닫기">×</button>
  </div>''',
'''    <div><h2 id="suziTitle">SUZI 무엇이든 물어보세요<sup><a href="#fn" id="fnLink" style="color:inherit;text-decoration:none">*</a></sup></h2><p>호텔 · 경로 · 명소 · 항공권 · 핫 키워드 · 최고 성능 모델로 답해요</p></div>
    <div class="hd-btns"><button class="x" id="gear" type="button" aria-label="SUZI 연결 설정">⚙</button><button class="x" id="close" type="button" aria-label="닫기">×</button></div>
  </div>
  <div class="connbar" id="connbar"></div>''')

# ---------- CSS ----------
rep('.stop{margin-left:8px;',
'''/* SUZI 연결 설정 */
.hd-btns{display:flex;gap:6px}
.connbar{flex:none;border-bottom:1px solid var(--line);padding:6px 16px;display:grid;gap:8px;font-size:12.5px;color:var(--muted)}
.connbar:empty{display:none}
.cstat .ok{color:var(--accent)} .cstat .no{color:var(--pin)}
.cstat .linkbtn{margin-left:6px}
.cform{display:grid;gap:8px;padding:4px 0 6px}
.cform label{display:grid;gap:3px;font-size:12px;color:var(--muted)}
.cform input,.cform select{font:inherit;font-size:15px;border:1px solid var(--line);border-radius:10px;padding:7px 10px;background:var(--bg);color:var(--fg);width:100%}
.cform .row{display:flex;gap:8px;align-items:center}
.cform .send{padding:8px 14px;border-radius:10px}
.cform .fine{padding:0}
.stop{margin-left:8px;''')

# ---------- 연결 어댑터 ----------
rep('''let sample=null, toolsOK=false, busy=false, ctl=null, turns=[], tierNoted=false;
(async()=>{
  try{ sample = window.claude ? await claude.use("sample") : null; }catch(e){ sample=null; }
  if(!sample){ fab.querySelector('.face').nextSibling.textContent='SUZI (이 화면에선 쉬는 중)'; return; }
  try{ const lim=await sample.limits(); toolsOK=!!lim.tools; }catch(e){ toolsOK=false; }
})();''',
r'''let sample=null, toolsOK=false, busy=false, ctl=null, turns=[], tierNoted=false;

// ---- SUZI 연결: ① claude.ai 아티팩트(sample) ② 외부 서버(프록시) ③ API 키 직접(테스트용) ----
// 공유 전에 아래 url/token을 적어 두면, 받는 사람은 설정 없이 바로 SUZI를 쓸 수 있어요.
const SUZI_DEFAULT={url:"",token:"",model:"claude-opus-5-5"};
const CONN_KEY="suzi-hk-conn-v1";
let CONN={mode:"auto",url:SUZI_DEFAULT.url,token:SUZI_DEFAULT.token,key:"",model:SUZI_DEFAULT.model};
try{ const c=JSON.parse(localStorage.getItem(CONN_KEY)||"null"); if(c&&typeof c==="object") CONN={...CONN,...c}; }catch(e){}
function saveConn(){ try{ localStorage.setItem(CONN_KEY, JSON.stringify(CONN)); }catch(e){} }
let BACKEND=null, connOpen=false;
function setFabLabel(t){ fab.querySelector('.face').nextSibling.textContent=t; }
async function connect(){
  BACKEND=null; sample=null; toolsOK=false;
  if(CONN.mode==="auto"){
    try{ sample = window.claude ? await claude.use("sample") : null; }catch(e){ sample=null; }
    if(sample){ BACKEND={kind:"artifact",label:"Claude 아티팩트"}; try{ const lim=await sample.limits(); toolsOK=!!lim.tools; }catch(e){ toolsOK=false; } }
  }
  if(!BACKEND&&CONN.mode!=="key"&&CONN.url){ BACKEND={kind:"proxy",label:"외부 서버"}; toolsOK=true; }
  if(!BACKEND&&CONN.mode!=="proxy"&&CONN.key){ BACKEND={kind:"key",label:"API 키 직접"}; toolsOK=true; }
  setFabLabel(BACKEND?'SUZI에게 물어보기':'SUZI 연결 설정');
  renderConnBar();
  return BACKEND;
}
function renderConnBar(){
  const el=document.getElementById('connbar'); if(!el) return;
  const st=BACKEND?`연결됨 · ${esc(BACKEND.label)}${BACKEND.kind!=="artifact"?' · '+esc(CONN.model):''}`:'연결 안 됨 · 설정이 필요해요';
  el.innerHTML=`<div class="cstat"><span class="${BACKEND?'ok':'no'}">●</span> ${st}<button class="linkbtn" type="button" id="connToggle">${connOpen?'설정 닫기':'연결 설정'}</button></div>`+(connOpen?`<form class="cform" id="cform" autocomplete="off">
   <label>연결 방식 <select id="cMode"><option value="auto">자동 (아티팩트 → 서버 → 키 순서)</option><option value="proxy">외부 서버(프록시)</option><option value="key">API 키 직접 (본인 테스트용)</option></select></label>
   <label>서버 주소 <input id="cUrl" type="url" placeholder="https://suzi-proxy.….workers.dev" inputmode="url" autocapitalize="off" spellcheck="false"></label>
   <label>서버 토큰 (선택) <input id="cTok" type="password" placeholder="서버를 만들 때 정한 토큰"></label>
   <label>API 키 (직접 방식만) <input id="cKey" type="password" placeholder="sk-ant-… 이 기기에만 저장돼요"></label>
   <label>모델 <select id="cModel"><option value="claude-opus-5-5">claude-opus-5-5 (추천 · 가장 똑똑)</option><option value="claude-sonnet-5-5">claude-sonnet-5-5 (빠름)</option><option value="claude-haiku-5-5">claude-haiku-5-5 (가장 빠름)</option></select></label>
   <div class="row"><button class="send" type="submit">저장하고 연결</button><button class="ghost" type="button" id="cClear">지우기</button></div>
   <p class="fine">주소·토큰·키는 이 기기 브라우저에만 저장돼요. API 키 직접 방식은 키가 노출될 수 있으니 공유용 파일에는 넣지 말고 본인 테스트에만 쓰세요.</p></form>`:'');
  document.getElementById('connToggle').onclick=()=>{ connOpen=!connOpen; renderConnBar(); };
  const f=document.getElementById('cform'); if(!f) return;
  f.querySelector('#cMode').value=CONN.mode; f.querySelector('#cUrl').value=CONN.url||''; f.querySelector('#cTok').value=CONN.token||''; f.querySelector('#cKey').value=CONN.key||''; f.querySelector('#cModel').value=CONN.model||'claude-opus-5-5';
  f.onsubmit=async e=>{ e.preventDefault();
    CONN={mode:f.querySelector('#cMode').value,url:f.querySelector('#cUrl').value.trim(),token:f.querySelector('#cTok').value.trim(),key:f.querySelector('#cKey').value.trim(),model:f.querySelector('#cModel').value};
    saveConn(); connOpen=false; const b=await connect();
    bubble('sys', b?`SUZI 연결됨 · ${b.label}`:'아직 연결되지 않았어요. 서버 주소나 키를 확인해 주세요');
  };
  f.querySelector('#cClear').onclick=async()=>{ CONN={mode:"auto",url:SUZI_DEFAULT.url,token:SUZI_DEFAULT.token,key:"",model:SUZI_DEFAULT.model}; saveConn(); await connect(); };
}
document.getElementById('gear').onclick=()=>{ connOpen=!connOpen; renderConnBar(); };
connect();

// ---- Claude Messages API 직접 호출 (외부 서버 또는 API 키) : 아티팩트 sample()과 같은 모양으로 ----
function httpCode(st){ return st===401||st===403?"not_granted":st===429?"rate_limited":st===400?"invalid_request":st===413?"prompt_too_large":"upstream_error"; }
async function apiRequest(body, headers, signal, onDelta){
  const url = BACKEND.kind==="key" ? "https://api.anthropic.com/v1/messages" : CONN.url;
  let resp;
  try{ resp=await fetch(url,{method:"POST",headers,body:JSON.stringify(body),signal}); }
  catch(e){ if(e&&e.name==="AbortError") throw {code:"cancelled",message:"cancelled"}; throw {code:"upstream_error",message:String(e&&e.message||e)}; }
  if(!resp.ok){ let msg=""; try{ const j=await resp.json(); msg=(j.error&&j.error.message)||""; }catch(e){} throw {code:httpCode(resp.status),message:msg||("HTTP "+resp.status)}; }
  const reader=resp.body.getReader(), dec=new TextDecoder(); let buf="", stop=null; const blocks=[];
  const handle=j=>{
    if(j.type==="content_block_start"){ const c=j.content_block; blocks[j.index]= c.type==="tool_use"?{type:"tool_use",id:c.id,name:c.name,_json:""}: c.type==="thinking"?{type:"thinking",thinking:"",signature:""}: c.type==="text"?{type:"text",text:""}: {...c}; }
    else if(j.type==="content_block_delta"){ const b=blocks[j.index], d=j.delta; if(!b||!d) return;
      if(d.type==="text_delta"){ b.text+=d.text; onDelta&&onDelta(d.text); }
      else if(d.type==="input_json_delta") b._json+=d.partial_json||"";
      else if(d.type==="thinking_delta") b.thinking+=d.thinking||"";
      else if(d.type==="signature_delta") b.signature+=d.signature||""; }
    else if(j.type==="message_delta"){ if(j.delta&&j.delta.stop_reason) stop=j.delta.stop_reason; }
    else if(j.type==="error"){ throw {code:"upstream_error",message:(j.error&&j.error.message)||"stream error"}; }
  };
  try{
    while(true){ const {value,done}=await reader.read(); if(done) break; buf+=dec.decode(value,{stream:true});
      let i; while((i=buf.indexOf("\n\n"))>=0){ const chunk=buf.slice(0,i); buf=buf.slice(i+2);
        for(const line of chunk.split("\n")){ if(!line.startsWith("data:")) continue; const s=line.slice(5).trim(); if(!s) continue; let j=null; try{ j=JSON.parse(s); }catch(e){ continue; } handle(j); } } }
  }catch(e){ if(e&&e.name==="AbortError") throw {code:"cancelled",message:"cancelled"}; throw e; }
  blocks.forEach(b=>{ if(b&&b.type==="tool_use"){ try{ b.input=JSON.parse(b._json||"{}"); }catch(e){ b.input={}; b._bad=true; } delete b._json; } });
  return {content:blocks.filter(Boolean), stop_reason:stop};
}
async function apiChat(msgs, opts){
  const sys=msgs[0].content; const conv=msgs.slice(1).map(m=>({role:m.role,content:m.content}));
  const tools=(opts.tools||[]).map(t=>({name:t.name,description:t.description,input_schema:t.inputSchema||{type:"object",properties:{}}}));
  const byName=Object.fromEntries((opts.tools||[]).map(t=>[t.name,t]));
  const model=CONN.model||"claude-opus-5-5";
  const headers={"content-type":"application/json","anthropic-version":"2023-06-01"};
  if(BACKEND.kind==="key"){ headers["x-api-key"]=CONN.key; headers["anthropic-dangerous-direct-browser-access"]="true"; }
  else if(CONN.token) headers["authorization"]="Bearer "+CONN.token;
  const useFallback=/^claude-(opus-5-5|opus-5|sonnet-5-5|fable-5-1)$/.test(model);
  if(useFallback) headers["anthropic-beta"]="server-side-fallback-2026-07-01";
  let full="", truncated=false;
  for(let round=0; round<6; round++){
    const body={model,max_tokens:8000,stream:true,system:sys,messages:conv,output_config:{effort:"high"}};
    if(tools.length) body.tools=tools;
    if(useFallback) body.fallbacks="default";
    const r=await apiRequest(body, headers, opts.signal, t=>{ full+=t; opts.onText&&opts.onText({text:full,delta:t}); });
    if(r.stop_reason==="refusal") throw {code:"refused",message:"refused",text:full||undefined};
    if(r.stop_reason==="max_tokens") truncated=true;
    const uses=r.content.filter(b=>b.type==="tool_use");
    if(r.stop_reason!=="tool_use"||!uses.length) break;
    conv.push({role:"assistant",content:r.content.map(b=> b.type==="text"?(b.text?{type:"text",text:b.text}:null): b.type==="thinking"?(b.signature?{type:"thinking",thinking:b.thinking,signature:b.signature}:null): b.type==="tool_use"?{type:"tool_use",id:b.id,name:b.name,input:b.input}: b).filter(Boolean)});
    const results=[];
    for(const u of uses){
      try{ if(u._bad) throw new Error("도구 입력 JSON이 잘못됐어요"); const t=byName[u.name]; if(!t) throw new Error("없는 도구예요");
        const out=await t.execute(u.input||{},{signal:opts.signal}); results.push({type:"tool_result",tool_use_id:u.id,content:JSON.stringify(out===undefined?{ok:true}:out)}); }
      catch(e){ results.push({type:"tool_result",tool_use_id:u.id,content:"Error: "+String(e&&e.message||e),is_error:true}); }
    }
    conv.push({role:"user",content:results});
    if(full&&!full.endsWith("\n\n")) full+="\n\n";
  }
  if(!full.trim()) throw {code:"empty_completion",message:"no text"};
  return {text:full, truncated, modelTierApplied:"complex"};
}''')

# ---------- ask(): 백엔드 분기 ----------
rep('''if(!sample){ bubble('ai',md("지금 이 화면에서는 SUZI가 연결되지 않았어요. Claude 앱이나 claude.ai에서 이 페이지를 열면 대화할 수 있어요.")); return; }''',
'''if(!BACKEND){ bubble('ai',md("아직 SUZI가 연결되지 않았어요. 세 가지 중 하나로 연결할 수 있어요.\\n- claude.ai 아티팩트 링크로 이 페이지를 열기 (로그인만 하면 돼요)\\n- 위 \\"연결 설정\\"에 외부 서버 주소 넣기 (공유용 추천)\\n- API 키 직접 넣기 (본인 테스트용)")); connOpen=true; renderConnBar(); return; }''')
rep('''const res=await sample([{role:"user",content:RULES()},...turns],opts); const {text:ans,truncated}=res;''',
'''const msgs=[{role:"user",content:RULES()},...turns];
    const res= BACKEND.kind==="artifact" ? await sample(msgs,opts) : await apiChat(msgs,opts); const {text:ans,truncated}=res;''')
rep('''if(e&&(e.code==="not_granted"||e.code==="sampling_disabled")) sample=null;''',
'''if(e&&(e.code==="not_granted"||e.code==="sampling_disabled")){ if(BACKEND&&BACKEND.kind==="artifact") sample=null; else { connOpen=true; renderConnBar(); } }''')
rep('''const ERR={not_granted:"SUZI 사용이 허용되지 않았어요. 아티팩트 권한에서 Claude 사용을 허용하면 다시 쓸 수 있어요.",''',
'''const ERR={not_granted:"SUZI 사용이 허용되지 않았어요. 아티팩트에선 권한에서 Claude 사용을 허용하고, 외부 서버·키 방식에선 연결 설정의 주소·토큰·키를 확인해 주세요.",invalid_request:"요청 형식이 맞지 않아요. 연결 설정의 모델 이름을 확인해 주세요.",upstream_error:"서버가 잠깐 불안정해요. 조금 뒤 다시 보내 주세요.",empty_completion:"답을 만들지 못했어요. 질문을 조금 바꿔 다시 물어봐 주세요.",''')
rep('''function hello(){ bubble('ai',md("안녕하세요, 모녀 여행 도우미 **SUZI**예요. 깡총!\\n호텔, 경로, 명소, 항공권, 요즘 핫한 키워드까지 물어보세요.\\n\\"Day 2에 ○○ 넣어줘\\", \\"마카오를 Day 2로 옮겨줘\\"처럼 말하면 일정에 바로 반영할게요.")); }''',
'''function hello(){ bubble('ai',md("안녕하세요, 모녀 여행 도우미 **SUZI**예요. 깡총!\\n호텔, 경로, 명소, 항공권, 요즘 핫한 키워드까지 물어보세요.\\n\\"Day 2에 ○○ 넣어줘\\", \\"마카오를 Day 2로 옮겨줘\\"처럼 말하면 일정에 바로 반영할게요.")); if(!BACKEND){ connOpen=true; renderConnBar(); } }''')

io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("ok", len(src))
