#!/usr/bin/env python3
"""その週の Issue 本文を標準出力へ。
   チェックボックスはトラック単位。issue_sync.py がこれを読みます。
   python3 scripts/gen_issue.py [週番号]"""
import json, sys
from pathlib import Path

st = json.loads((Path(__file__).resolve().parents[1] / "docs" / "state.json").read_text(encoding="utf-8"))
w = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].strip() else st["current"]
r = next(x for x in st["weeks"] if x["w"] == w)

out = [f'**{r["start"]} 〜 {r["end"]} ／ {r["phase"]}** ・ 配分 **{r["budget"]}h**', ""]

if r["links"]:
    out.append("**今週つながっているもの**")
    for x in r["links"]:
        out.append(f"- {x}")
    out.append("")

out.append("## トラック")
for t in r["tracks"]:
    mark = "x" if t["done"] else " "
    if t["unit"]:
        u = t["unit"]
        body = f'{t["label"]} — {u["subject"]}{u["unit"]} {u["short"]}（{" / ".join(u["chapters"])}）'
    else:
        body = f'{t["label"]}' + (f' — {t["note"]}' if t.get("note") else "")
    out.append(f"- [{mark}] {body}")

out += ["", "## 進めかたの目安", ""]
for t in r["task_list"]:
    out.append(f"- {t}")

out += ["", "```", f'hours: {r["hours"]}', "```", "",
        "<!-- 上のトラックにチェックを入れると data/log.yaml に反映されます -->"]
print("\n".join(out))
