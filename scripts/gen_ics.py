#!/usr/bin/env python3
"""docs/state.json → docs/plan.ics （Googleカレンダー / Apple カレンダーに取り込む）"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
st = json.loads((ROOT / "docs" / "state.json").read_text(encoding="utf-8"))


def esc(s):
    return str(s).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def fold(line):
    out, cur = [], line
    while len(cur.encode()) > 73:
        cut = 70
        while len(cur[:cut].encode()) > 73:
            cut -= 1
        out.append(cur[:cut])
        cur = " " + cur[cut:]
    out.append(cur)
    return "\r\n".join(out)


L = [
    "BEGIN:VCALENDAR", "VERSION:2.0",
    "PRODID:-//kenchikushi-2027//JP", "CALSCALE:GREGORIAN",
    "X-WR-CALNAME:" + esc(st["meta"]["title"]),
]

for r in st["weeks"]:
    s = date.fromisoformat(r["start"])
    e = s + timedelta(days=7)
    if r["new"]:
        n = r["new"]
        title = f'W{r["w"]:02d} {n["subject"]}{n["unit"]} {n["short"]}'
        desc = ["新規: " + " / ".join(n["chapters"])]
    else:
        title = f'W{r["w"]:02d} {r["phase"]}'
        desc = []
    if r.get("final_subject"):
        title = f'W{r["w"]:02d} {r["final_subject"]} 総まとめ'
        if r.get("final_extra"):
            desc.append("回収: " + " / ".join(r["final_extra"]))
    if r["review"]:
        desc.append(f'復習: {r["review"]["subject"]}{r["review"]["unit"]} {r["review"]["short"]}')
    if r["exam"]:
        desc.append(f'過去問: {r["exam"]["subject"]}{r["exam"]["unit"]} {r["exam"]["short"]}')
    desc.append(f'配分: {r["budget"]}h')
    for x in r.get("links", []):
        desc.append("連結: " + x)

    L += [
        "BEGIN:VEVENT",
        f'UID:w{r["w"]:02d}@kenchikushi-2027',
        f'DTSTART;VALUE=DATE:{s.strftime("%Y%m%d")}',
        f'DTEND;VALUE=DATE:{e.strftime("%Y%m%d")}',
        fold("SUMMARY:" + esc(title)),
        fold("DESCRIPTION:" + esc("\n".join(desc))),
        "TRANSP:TRANSPARENT",
        "END:VEVENT",
    ]

for m in st["milestones"]:
    wk = next(x for x in st["weeks"] if x["w"] == m["week"])
    d = date.fromisoformat(wk["start"])
    if m["name"] == "本試験":
        d = date.fromisoformat(st["meta"]["exam_date"])
    L += [
        "BEGIN:VEVENT",
        f'UID:ms{m["week"]}@kenchikushi-2027',
        f'DTSTART;VALUE=DATE:{d.strftime("%Y%m%d")}',
        f'DTEND;VALUE=DATE:{(d + timedelta(days=1)).strftime("%Y%m%d")}',
        fold("SUMMARY:★ " + esc(m["name"])),
        fold("DESCRIPTION:" + esc(m.get("note", ""))),
        "BEGIN:VALARM", "TRIGGER:-P7D", "ACTION:DISPLAY",
        fold("DESCRIPTION:" + esc(m["name"] + " まで1週間")), "END:VALARM",
        "END:VEVENT",
    ]

L.append("END:VCALENDAR")
(ROOT / "docs" / "plan.ics").write_text("\r\n".join(L) + "\r\n", encoding="utf-8")
print("wrote docs/plan.ics")
