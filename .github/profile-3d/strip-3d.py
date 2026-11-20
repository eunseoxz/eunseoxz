#!/usr/bin/env python3
"""Keep only the 3D contribution city and the contribution count.

Post-processes the SVG written by yoshi389111/github-profile-3d-contrib
(pinned v0.9.3). Removes the radar chart, the language pie, star/fork
counters and the date range. Usage: strip-3d.py <in.svg> [out.svg]
"""
import sys
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
q = lambda t: "{%s}%s" % (NS, t)

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src
tree = ET.parse(src)
root = tree.getroot()

groups = [c for c in root if c.tag == q("g")]
if not groups:
    sys.exit("strip-3d: no groups found, layout changed?")
city = groups[0]
for g in groups[1:]:
    texts = [t.text or "" for t in g.iter(q("text"))]
    if "contributions" in texts or any(t.attrib.get("class") == "fill-strong" for t in g.iter(q("text"))):
        # stats row: keep only the big number (fill-strong) and its label
        keep = []
        kids = list(g)
        for i, k in enumerate(kids):
            if k.tag == q("text") and k.attrib.get("class") == "fill-strong":
                keep = [k] + ([kids[i + 1]] if i + 1 < len(kids) else [])
                break
        for k in kids:
            if k not in keep:
                g.remove(k)
    else:
        root.remove(g)  # radar chart or language pie

out = ET.tostring(root, encoding="unicode")
for bad in ("<script", "<foreignObject", "href=\"http"):
    if bad in out:
        sys.exit("strip-3d: unexpected %s" % bad)
with open(dst, "w", encoding="utf-8") as f:
    f.write(out)
print("strip-3d: kept city + count ->", dst)
