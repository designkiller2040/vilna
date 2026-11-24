#!/usr/bin/env python3
"""Turn a file saved with the site's "export" button into works.js (+ pictures in images/).

usage: python3 import-works.py path/to/vilna-works.json

Every page (the file on disk, the local preview, the live site) loads works.js,
so after this they all show the same pictures and notes.
"""
import base64, json, re, sys, time
from pathlib import Path

here = Path(__file__).resolve().parent
data = json.loads(Path(sys.argv[1]).read_text())
items = data["items"] if isinstance(data, dict) else data
keep = ("id", "kind", "tag", "name", "title", "text", "src", "x", "y", "z", "t", "c", "ar")
out = []
for it in items:
    du = it.pop("dataUrl", None)
    if du:  # a picture that only lived in the browser: save it as a file next to the others
        m = re.match(r"data:image/(\w+)[^,]*;base64,(.*)", du, re.S)
        ext = {"jpeg": "jpg", "svg+xml": "svg"}.get(m.group(1), m.group(1))
        slug = re.sub(r"[^a-z0-9]+", "-", (it.get("name") or "picture").lower()).strip("-") or "picture"
        name = f"{slug}-{it['id'][:6]}.{ext}"
        (here / "images" / name).write_bytes(base64.b64decode(m.group(2)))
        it["src"] = "images/" + name
    if it.get("kind") != "note" and not it.get("src"):
        continue
    out.append({k: it[k] for k in keep if it.get(k) not in (None, "")})

works = {"v": int(time.time()), "items": out}
(here / "works.js").write_text(
    "// pictures and notes shown on every copy of the site (made by import-works.py)\n"
    "window.WORKS = " + json.dumps(works, ensure_ascii=False, indent=1) + ";\n")
print(f"works.js: {len(out)} items")
