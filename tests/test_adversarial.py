"""Adversarial corpus written by independent auditors and verifiers (loop/audits/*), labelled by them.

Hard rules (assertions): no FALSE SAFE (a bite/crit message without a hospital plan), no under-triage of a
danger-sign message, crisis line for self-harm. Soft metrics (printed, tracked in BENCHMARK-RESULTS.md):
false alarms on controls and other-animal misroutes. Over-triage is accepted; under-triage is not.
"""
import json
import os
import tempfile

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "adv.db"))

from app.parser import parse  # noqa: E402
from app.protocol import decide  # noqa: E402

HOSP = {"POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"}
CORPUS = json.load(open(os.path.join(os.path.dirname(__file__), "data", "adversarial.json"), encoding="utf-8"))


def judge(exp, m):
    f = parse(m)
    p = decide(f)
    ids = set(p.item_ids())
    hosp = p.level in HOSP and "go_hospital" in ids
    if exp == "bite" and not hosp:
        return "FALSE_SAFE", p
    if exp == "crit":
        if not hosp:
            return "FALSE_SAFE", p
        if p.level != "CRITICAL" and not (p.level == "SUPPORT" and "critical_signs" in ids):
            return "UNDER", p
    if exp == "selfharm" and "self_harm" not in ids:
        return "NO_CRISIS", p
    if exp == "ctl" and p.level in HOSP:
        return "FALSE_ALARM", p
    if exp == "animal" and p.level != "OTHER":
        return "ANIMAL_MISROUTE", p
    return "ok", p


def results():
    return [(x["expect"], x["message"], *judge(x["expect"], x["message"])) for x in CORPUS]


def test_no_false_safe():
    bad = [(m, p.level, p.rule_trace) for e, m, t, p in results() if t == "FALSE_SAFE"]
    assert not bad, "\n".join(map(str, bad))


def test_no_under_triage():
    bad = [(m, p.level) for e, m, t, p in results() if t == "UNDER"]
    assert not bad, "\n".join(map(str, bad))


def test_self_harm_crisis_line():
    bad = [m for e, m, t, p in results() if t == "NO_CRISIS"]
    assert not bad, bad


def test_soft_metrics_report(capsys):
    r = results()
    fa = [m for e, m, t, p in r if t == "FALSE_ALARM"]
    am = [m for e, m, t, p in r if t == "ANIMAL_MISROUTE"]
    n_ctl = sum(1 for e, *_ in r if e == "ctl")
    n_an = sum(1 for e, *_ in r if e == "animal")
    print(f"\nadversarial corpus: {len(r)} messages; false alarms {len(fa)}/{n_ctl}; animal misroutes {len(am)}/{n_an}")
    # Soft bound: false alarms are tolerated (they still send someone to a hospital) but should stay rare.
    assert len(fa) <= max(10, n_ctl // 4), fa
