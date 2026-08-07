#!/usr/bin/env python3
"""Issue のトラックのチェックを data/log.yaml へ反映する。
   環境変数 ISSUE_TITLE / ISSUE_BODY を読みます。"""
import os, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "data" / "log.yaml"

LABELS = {"新規": "new", "復習": "review", "過去問": "exam", "累積": "cum",
          "模試": "test", "総まとめ": "final", "年度別": "years"}

title = os.environ.get("ISSUE_TITLE", "")
body = os.environ.get("ISSUE_BODY", "")

m = re.search(r"W(\d{1,2})", title)
if not m:
    print("週番号が見つかりません:", title)
    sys.exit(0)
key = f"W{int(m.group(1)):02d}"

found = {}
for checked, text in re.findall(r"^\s*- \[([ xX])\]\s*(.+)$", body, re.M):
    for jp, k in LABELS.items():
        if text.startswith(jp):
            found[k] = checked.lower() == "x"
            break

hours = None
h = re.search(r"hours:\s*([\d.]+)", body)
if h:
    hours = float(h.group(1))
    if hours == int(hours):
        hours = int(hours)

text = LOG.read_text(encoding="utf-8")
log = yaml.safe_load(text) or {}
entry = log.get(key) or {}
if entry.get("status") == "slipped":
    print(f"{key} は slipped。手で直してください。")
    sys.exit(0)

entry.update(found)
if hours is not None:
    entry["hours"] = hours
log[key] = entry

header = "\n".join(l for l in text.splitlines() if l.startswith("#") or not l.strip())
out = [header.rstrip(), ""]
order = ["status", "new", "review", "exam", "cum", "test", "final", "years",
         "hours", "moved_to", "memo"]
for k in sorted(log, key=lambda x: int(re.sub(r"\D", "", x) or 0)):
    v = log[k] or {}
    out.append(f"{k}:")
    for f in order:
        if v.get(f) is not None and v.get(f) != "":
            out.append(f"  {f}: {str(v[f]).lower() if isinstance(v[f], bool) else v[f]}")
    if v.get("exam_note"):
        e = v["exam_note"]
        out.append(f'  exam_note: {{ set: {e.get("set")}, score: {e.get("score")} }}')
    out.append("")

LOG.write_text("\n".join(out), encoding="utf-8")
print(f'{key}: ' + ", ".join(f"{k}={v}" for k, v in found.items()))
