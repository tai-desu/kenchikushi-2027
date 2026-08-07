#!/usr/bin/env python3
"""Issue のタイトルを出力。 python3 scripts/issue_title.py [週番号]"""
import json, sys
from pathlib import Path
st = json.loads((Path(__file__).resolve().parents[1] / "docs" / "state.json").read_text(encoding="utf-8"))
a = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else None
w = int(a) if a else st["current"]
r = next(x for x in st["weeks"] if x["w"] == w)
n = r["new"]
print(f'W{w:02d} ' + (f'{n["subject"]}{n["unit"]} {n["short"]}' if n else r["phase"]))
