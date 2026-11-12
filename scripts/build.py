#!/usr/bin/env python3
"""
plan.yaml + log.yaml  →  docs/state.js / docs/state.json

週の中身は plan.yaml の schedule: で決まります（1週に複数単元も可）。
state は毎回ゼロから計算し直します。壊れても再生成できます。
    python3 scripts/build.py
"""
import json
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"


def load(name):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


plan = load("plan.yaml")
log = load("log.yaml")

ROT = plan["rotation"]
SUBJ = plan["subjects"]
UNITS = plan["units"]
START = plan["meta"]["start_date"]
NW = plan["meta"]["total_weeks"]
AVG_W = sum(s["weight"] for s in SUBJ.values()) / len(SUBJ)
SCHED = {int(k): (v or {}) for k, v in (plan.get("schedule") or {}).items()}
PRIOR = plan.get("prior") or {}
LINKS = plan.get("links") or {}
TEMPL = plan["task_template"]
FINAL = plan.get("final_review") or {}


def week_start(n):
    return START + timedelta(days=7 * (n - 1))


def uinfo(subject, unit):
    u = UNITS[subject][int(unit)]
    s = SUBJ[subject]
    return {
        "subject": subject,
        "ch": s["ch"],
        "color": s["color"],
        "unit": int(unit),
        "short": u["short"],
        "chapters": u["chapters"],
    }


def units_of(pairs):
    return [uinfo(s, n) for s, n in (pairs or [])]


def new_of(w):
    return units_of(SCHED.get(w, {}).get("new"))


def prev_new(w, k):
    """w より前で「新規」がある週を遡って k 個ぶん返す（各要素は単元のリスト）。
       テスト週・予備週を飛び越えてトラックをつなぐ。"""
    out = []
    x = w - 1
    while x >= 1 and len(out) < k:
        n = new_of(x)
        if n:
            out.append(n)
        x -= 1
    while len(out) < k:
        out.append([])
    return out


def phase_of(w):
    for p in plan["phases"]:
        a, b = p["weeks"]
        if a <= w <= b:
            return p
    return plan["phases"][-1]


prior_units = [uinfo(s, n) for s in ROT for n in (PRIOR.get(s) or [])]

weeks = []
for w in range(1, NW + 1):
    p = phase_of(w)
    typ = p.get("type", "study")
    sc = SCHED.get(w, {})
    new = new_of(w)
    entry = log.get(f"W{w:02d}") or {}

    rv, ex = prev_new(w, 2)
    if "review" in sc:
        rv = units_of(sc["review"])
    if "exam" in sc:
        ex = units_of(sc["exam"])
    if typ in ("final", "prior"):
        rv, ex = [], []

    wsum = sum(SUBJ[u["subject"]]["weight"] for u in new)
    budget = round(p.get("hours", 0) * (wsum / AVG_W if new else 1), 1)

    # ── トラック単位の完了。これが進捗の実体 ──────────
    tr = []

    def add(key, label, units=None, note=None):
        tr.append({
            "key": key, "label": label, "units": units or [], "note": note,
            "done": bool(entry.get(key, False)),
        })

    if typ == "midterm":
        add("test", "模試", None, f'{p["questions"]}問' if p.get("questions") else None)
    if typ == "final":
        add("final", "総まとめ", None, "全8単元の速習")
        add("years", "年度別", None, "10年分")
    if new:
        add("new", "新規", new)
    if rv:
        add("review", "復習", rv)
    if ex:
        add("exam", "過去問", ex)
    if new or typ in ("midterm", "bridge"):
        add("cum", "累積", None, "既習範囲から20問")

    done = sum(1 for x in tr if x["done"])
    if typ == "prior":
        status = "done"
    elif entry.get("status") == "slipped":
        status = "slipped"
    else:
        status = entry.get("status") or (
            "done" if tr and done == len(tr) else ("in_progress" if done else "planned")
        )

    rnd = sc.get("round")
    rec = {
        "w": w,
        "start": week_start(w).isoformat(),
        "end": (week_start(w) + timedelta(days=6)).isoformat(),
        "phase": p["name"],
        "type": typ,
        "round": rnd,
        "new": new,
        "review": rv,
        "exam": ex,
        "budget": budget,
        "status": status,
        "tasks_done": done,
        "tasks_total": len(tr),
        "tracks": tr,
        "task_list": TEMPL.get(typ) or TEMPL["default"],
        "hours": entry.get("hours", 0),
        "moved_to": entry.get("moved_to"),
        "memo": entry.get("memo"),
        "links": LINKS.get(rnd, []) if rnd else [],
    }
    if typ == "final" and w in FINAL:
        rec["final_subject"] = FINAL[w]["subject"]
        rec["final_extra"] = FINAL[w].get("extra", [])
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

units_total = sum(len(v) for v in UNITS.values())
units_done = len(prior_units) + sum(
    len(r["new"]) for r in weeks
    if any(t["key"] == "new" and t["done"] for t in r["tracks"])
)

nxt = next(
    (m for m in plan["milestones"] if m["week"] >= current),
    plan["milestones"][-1],
)

state = {
    "meta": plan["meta"],
    "subjects": SUBJ,
    "rotation": ROT,
    "generated": today.isoformat(),
    "current": current,
    "prior": prior_units,
    "weeks": weeks,
    "milestones": plan["milestones"],
    "summary": {
        "done": done_n,
        "slipped": slip_n,
        "remaining": NW - done_n,
        "pct": round(units_done / units_total * 100) if units_total else 0,
        "units_done": units_done,
        "units_total": units_total,
        "hours_total": round(sum(r["budget"] for r in weeks)),
        "hours_left": hours_left,
        "hours_logged": sum(r["hours"] or 0 for r in weeks),
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
print(f"built  weeks={len(weeks)}  current=W{current}  units={units_done}/{units_total}  left={hours_left}h")
