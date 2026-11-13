#!/usr/bin/env python3
"""Run the scenario library against a deployment and write a results bundle.

usage: python3 scripts/run_eval.py https://dansh.example.org [--out eval_results]

Every request carries `x-dansh-test: 1`, so evaluation traffic is never counted
in the public impact numbers.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import httpx
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BITE_LEVELS = {"POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"}
ALWAYS_FOR_BITES = ["call_108", "go_hospital", "dont_tourniquet", "dont_cut_suck", "dont_healer"]


def run(base: str, cases_path: str) -> dict:
    cases = yaml.safe_load(open(cases_path, encoding="utf-8"))
    results = []
    with httpx.Client(base_url=base.rstrip("/"), timeout=30, headers={"x-dansh-test": "1"}) as c:
        health = c.get("/api/health").json()
        for case in cases:
            t0 = time.time()
            r = c.post("/api/consult", json={"message": case["message"]})
            ms = int((time.time() - t0) * 1000)
            body = r.json()
            got_level = body.get("level")
            ids = set(body.get("item_ids", []))
            exp = case["expect"]
            problems = []
            if got_level != exp["level"]:
                problems.append(f"level {got_level} != {exp['level']}")
            for i in exp.get("include", []):
                if i not in ids:
                    problems.append(f"missing {i}")
            for i in exp.get("exclude", []):
                if i in ids:
                    problems.append(f"should not include {i}")
            safety = []
            if case["group"] == "bite":
                if got_level not in BITE_LEVELS:
                    safety.append("FALSE SAFE: bite case did not send to hospital")
                for i in ALWAYS_FOR_BITES:
                    if i not in ids:
                        safety.append(f"bite plan missing {i}")
            else:
                if got_level in BITE_LEVELS:
                    safety.append("false alarm: control case triggered the snakebite protocol")
            results.append({
                "id": case["id"], "lang": case["lang"], "group": case["group"], "message": case["message"],
                "expected_level": exp["level"], "got_level": got_level, "pass": not problems and not safety,
                "problems": problems, "safety": safety, "http": r.status_code, "ms": ms,
                "parser": body.get("parser", {}), "rule_trace": body.get("rule_trace", []),
            })
    bite = [x for x in results if x["group"] == "bite"]
    ctl = [x for x in results if x["group"] == "control"]
    rank = {"POSSIBLE": 1, "URGENT": 2, "CRITICAL": 3, "SUPPORT": 4}
    summary = {
        "cases": len(results),
        "passed": sum(x["pass"] for x in results),
        "false_safe": sum(1 for x in bite if x["got_level"] not in BITE_LEVELS),
        "bite_cases_sent_to_hospital": sum(1 for x in bite if x["got_level"] in BITE_LEVELS),
        "bite_cases": len(bite),
        "under_triage": sum(1 for x in bite if x["got_level"] in rank and x["expected_level"] in rank
                            and rank[x["got_level"]] < rank[x["expected_level"]]),
        "over_triage": sum(1 for x in bite if x["got_level"] in rank and x["expected_level"] in rank
                           and rank[x["got_level"]] > rank[x["expected_level"]]),
        "controls_correct": sum(1 for x in ctl if x["pass"]),
        "controls": len(ctl),
        "median_ms": sorted(x["ms"] for x in results)[len(results) // 2],
    }
    return {"base_url": base, "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "health": health, "summary": summary, "results": results}


def render(bundle: dict) -> str:
    s = bundle["summary"]
    lines = [
        f"Run against `{bundle['base_url']}` at {bundle['ran_at']} (app {bundle['health'].get('version')}, "
        f"LLM reader: {'on' if bundle['health'].get('llm') else 'off, keyword parser only'}).",
        "",
        f"- **{s['passed']}/{s['cases']}** cases matched the expected outcome exactly",
        f"- **{s['bite_cases_sent_to_hospital']}/{s['bite_cases']}** bite cases sent to hospital "
        f"(**{s['false_safe']} false safe**)",
        f"- under-triage (lower level than expected): **{s['under_triage']}** · over-triage: {s['over_triage']}",
        f"- controls correctly kept out of the snakebite protocol: **{s['controls_correct']}/{s['controls']}**",
        f"- median response time: {s['median_ms']} ms",
        "",
        "| # | case | lang | expected | got | result | notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(bundle["results"], 1):
        notes = "; ".join(r["problems"] + r["safety"]) or ""
        lines.append(f"| {i} | `{r['id']}` | {r['lang']} | {r['expected_level']} | {r['got_level']} | "
                     f"{'✅' if r['pass'] else '❌'} | {notes} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--cases", default=os.path.join(ROOT, "eval_cases", "cases.yaml"))
    ap.add_argument("--out", default=os.path.join(ROOT, "eval_results"))
    a = ap.parse_args()
    bundle = run(a.base, a.cases)
    os.makedirs(a.out, exist_ok=True)
    stamp = bundle["ran_at"].replace(":", "").replace("-", "")
    with open(os.path.join(a.out, f"run-{stamp}.json"), "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(a.out, "latest.json"), "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, ensure_ascii=False, indent=2)
    md = render(bundle)
    with open(os.path.join(a.out, "latest.md"), "w", encoding="utf-8") as fh:
        fh.write(md + "\n")
    print(md)
    sys.exit(0 if bundle["summary"]["false_safe"] == 0 else 1)


if __name__ == "__main__":
    main()
