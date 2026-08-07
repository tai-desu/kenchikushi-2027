#!/usr/bin/env python3
"""
plan.yaml + log.yaml + vault.yaml  →  docs/state.js / docs/state.json

state は毎回ゼロから計算し直します。壊れても再生成できます。
    python3 scripts/build.py
"""
import json, math, sys
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"


def load(name):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


plan = load("plan.yaml")
log = load("log.yaml") or {}

ROT = plan["rotation"]
SUBJ = plan["subjects"]
UNITS = plan["units"]
START = plan["meta"]["start_date"]
NW = plan["meta"]["total_weeks"]
AVG_W = sum(s["weight"] for s in SUBJ.values()) / len(SUBJ)


def week_start(n):
    return START + timedelta(days=7 * (n - 1))


def slot(w):
    """NEW スロット通し番号。中間・予備・直前期は None"""
    if w <= 20:
        return w
    if w <= 22:
        return None
    if w <= 42:
        return w - 2
    return None


def new_of(w):
    r = slot(w)
    if not r:
        return None
    subject = ROT[(r - 1) % len(ROT)]
    unit = math.ceil(r / len(ROT))
    return subject, unit


def unit_info(w):
    n = new_of(w)
    if not n:
        return None
    subject, unit = n
    u = UNITS[subject][unit]
    s = SUBJ[subject]
    return {
        "subject": subject,
        "ch": s["ch"],
        "color": s["color"],
        "unit": unit,
        "short": u["short"],
        "chapters": u["chapters"],
    }


def prev_units(w, k):
    """w より前で「新規」がある週を遡って k 個ぶん返す。
       中間テスト・予備週を飛び越えてトラックをつなぐ。"""
    out = []
    x = w - 1
    while x >= 1 and len(out) < k:
        i = unit_info(x)
        if i:
            out.append(i)
        x -= 1
    while len(out) < k:
        out.append(None)
    return out


def phase_of(w):
    for p in plan["phases"]:
        a, b = p["weeks"]
        if a <= w <= b:
            return p
    return plan["phases"][-1]


def tasks_for(w):
    t = plan["task_template"]
    p = phase_of(w)
    if p.get("type") == "midterm":
        return t["midterm"]
    if p.get("type") == "final":
        return t["final"]
    return t["default"]


weeks = []
for w in range(1, NW + 1):
    p = phase_of(w)
    info = unit_info(w)
    entry = log.get(f"W{w:02d}") or {}
    tasks = tasks_for(w)

    rv, ex = prev_units(w, 2)
    if p.get("type") == "final":
        rv = ex = None

    budget = round(p["hours"] * (SUBJ[info["subject"]]["weight"] if info else AVG_W) / AVG_W, 1)

    # ── トラック単位の完了。これが進捗の実体 ──────────
    tr = []
    def add(key, label, unit=None, note=None):
        tr.append({
            "key": key, "label": label, "unit": unit, "note": note,
            "done": bool(entry.get(key, False)),
        })

    if p.get("type") == "midterm":
        add("test", "模試", None, p.get("questions", 0) and f'{p["questions"]}問')
    if p.get("type") == "final":
        add("final", "総まとめ", None, "全8単元の速習")
        add("years", "年度別", None, "10年分")
    if info:
        add("new", "新規", info)
    if rv:
        add("review", "復習", rv)
    if ex:
        add("exam", "過去問", ex)
    if info or p.get("type") == "midterm":
        add("cum", "累積", None, "既習範囲から20問")

    done = sum(1 for x in tr if x["done"])
    status = entry.get("status") or (
        "done" if tr and done == len(tr) else ("in_progress" if done else "planned")
    )
    if entry.get("status") == "slipped":
        status = "slipped"

    rec = {
        "w": w,
        "start": week_start(w).isoformat(),
        "end": (week_start(w) + timedelta(days=6)).isoformat(),
        "phase": p["name"],
        "type": p.get("type", "study"),
        "round": math.ceil(slot(w) / 5) if slot(w) else None,
        "new": info,
        "review": rv,
        "exam": ex,
        "budget": budget,
        "status": status,
        "tasks_done": done,
        "tasks_total": max(1, len(tr)),
        "tracks": tr,
        "task_list": tasks,
        "hours": entry.get("hours", 0),
        "exam_result": entry.get("exam"),
        "moved_to": entry.get("moved_to"),
        "memo": entry.get("memo"),
    }
    if p.get("type") == "final" and w in plan.get("final_review", {}):
        fr = plan["final_review"][w]
        rec["final_subject"] = fr["subject"]
        rec["final_extra"] = fr.get("extra", [])
    rec["links"] = plan.get("links", {}).get(rec["round"], []) if rec["round"] else []
    weeks.append(rec)

# ── 現在週 ────────────────────────────────────────────
today = date.today()
current = 0
for r in weeks:
    if date.fromisoformat(r["start"]) <= today:
        current = r["w"]
current = max(1, current)

done_n = sum(1 for r in weeks if r["status"] == "done")
slip_n = sum(1 for r in weeks if r["status"] == "slipped")
hours_left = round(sum(r["budget"] for r in weeks if r["status"] != "done"))

nxt = next(
    (m for m in plan["milestones"] if m["week"] >= current),
    plan["milestones"][-1],
)

state = {
    "meta": plan["meta"],
    "subjects": SUBJ,
    "rotation": ROT,
    "generated": date.today().isoformat(),
    "current": current,
    "weeks": weeks,
    "milestones": plan["milestones"],
    "summary": {
        "done": done_n,
        "slipped": slip_n,
        "remaining": NW - done_n,
        "pct": round(done_n / NW * 100),
        "hours_total": round(sum(r["budget"] for r in weeks)),
        "hours_left": hours_left,
        "weeks_left": max(0, NW - current),
        "next_gate": nxt,
    },
}

DOCS.mkdir(exist_ok=True)
(DOCS / "state.json").write_text(
    json.dumps(state, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
)
# file:// でも開けるように JS 版も出す
(DOCS / "state.js").write_text(
    "window.STATE = " + json.dumps(state, ensure_ascii=False, default=str) + ";\n",
    encoding="utf-8",
)
print(f"built  weeks={len(weeks)}  current=W{current}  done={done_n}  left={hours_left}h")
