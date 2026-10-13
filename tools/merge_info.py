# -*- coding: utf-8 -*-
"""Merge verified info (info_part*.out.json) into INFO in index.html.
Rules: high/medium confidence → replace hours/fee, set site if given, add src + note.
       low confidence → keep original values, add note only.
Usage: python merge_info.py index.html scratchpad_dir"""
import sys, io, json, glob, re, os
path, sdir = sys.argv[1], sys.argv[2]
src = io.open(path, encoding="utf-8").read()
res = {}
for f in sorted(glob.glob(os.path.join(sdir, "info_part*.out.json"))):
    for e in json.load(io.open(f, encoding="utf-8")):
        res[e["q"]] = e

m = re.search(r'const INFO=\{\n(.*?)\n\};', src, re.S)
assert m
block = m.group(1)
lines = block.split("\n")
out = []
changed = 0
missing = []

def js(s):
    return json.dumps(s, ensure_ascii=False)

for line in lines:
    mm = re.match(r'^ "([^"]+)":\{(.*)\},?$', line)
    if not mm:
        out.append(line); continue
    q, body = mm.group(1), mm.group(2)
    e = res.get(q)
    if not e:
        missing.append(q); out.append(line); continue
    conf = (e.get("confidence") or "low").lower()
    def setf(body, key, val):
        val = js(val)
        if re.search(r'(^|,)' + key + r':', body):
            # replace existing string field  key:"..."
            return re.sub(r'(^|,)(' + key + r'):"(?:[^"\\]|\\.)*"', lambda k: k.group(1) + key + ':' + val, body, count=1)
        return body + "," + key + ":" + val
    if conf in ("high", "medium"):
        if e.get("hours"): body = setf(body, "hours", e["hours"])
        if e.get("fee"): body = setf(body, "fee", e["fee"])
        if e.get("site"): body = setf(body, "site", e["site"])
        if e.get("siteName"): body = setf(body, "siteName", e["siteName"])
        changed += 1
    if e.get("source"): body = setf(body, "src", e["source"])
    if e.get("note"): body = setf(body, "upd", e["note"])
    body = setf(body, "conf", conf)
    out.append(' ' + js(q) + ':{' + body + '}' + (',' if line.rstrip().endswith(',') else ''))

new_block = "\n".join(out)
src = src[:m.start(1)] + new_block + src[m.end(1):]
io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("merged", changed, "entries updated; missing:", missing)
