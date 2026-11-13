import itertools
import os
import random
import tempfile

os.environ["DANSH_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ["DANSH_MIN_PRE_SECS"] = "0"   # the timing filter is tested separately in test_integrity.py
os.environ["DANSH_MIN_POST_SECS"] = "0"
os.environ["DANSH_RATE_PER_MIN"] = "100000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import llm, quiz  # noqa: E402
from app.content import ITEMS, SOURCES  # noqa: E402
from app.main import app  # noqa: E402
from app.parser import Facts, parse  # noqa: E402
from app.protocol import check_invariants, decide  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------- content
def test_every_item_bilingual_and_sourced():
    for k, v in ITEMS.items():
        assert v["en"] and v["hi"], k
        assert v["src"] in SOURCES, k


# ---------------------------------------------------------------- parser
@pytest.mark.parametrize("msg,expect", [
    ("papa ko saanp ne kaata 10 minute pehle", {"snake": True, "lang": "hi", "minutes_since": 10}),
    ("साँप ने काटा", {"snake": True, "lang": "hi"}),
    ("सांप ने काटा", {"snake": True}),
    ("a cobra bit my brother 2 hours ago", {"snake": True, "minutes_since": 120}),
    ("snake bite, we tied a rope tightly", {"done_tourniquet": True}),
    ("took him to the ojha for jhaad phoonk", {"done_healer": True}),
    ("no breathing problem, no bleeding", {"red_flags": []}),
    ("dog bit me", {"other_animal": "dog", "snake": False}),
    ("I feel a bit tired", {"bite": False}),
])
def test_parse(msg, expect):
    f = parse(msg).to_dict()
    for k, v in expect.items():
        assert f[k] == v, (msg, k, f[k])


@pytest.mark.parametrize("msg,flag,present", [
    ("snake bit him, he is not breathing", "breathing", True),
    ("saanp ne kaata, saans nahi aa rahi", "breathing", True),
    ("साँप ने काटा, सांस नहीं ले पा रहा", "breathing", True),
    ("snake bit him, can't open eyes", "ptosis", True),
    ("snake bit him, not responding", "unconscious", True),
    ("snake bite, no bleeding", "bleeding", False),
    ("saanp ne kaata, khoon nahi aa raha", "bleeding", False),
    ("snake bite, breathing is normal", "breathing", False),
    ("saanp ne kaata, saans theek hai", "breathing", False),
    ("snake bite, no bleeding but now bleeding from gums", "bleeding", True),
])
def test_negation_is_safe(msg, flag, present):
    assert (flag in parse(msg).red_flags) is present, msg


def test_negation_is_recorded():
    f = parse("snake bit him, no difficulty breathing")
    assert "breathing" not in f.red_flags and "breathing" in f.negated


# ---------------------------------------------------------------- protocol safety
def test_red_flag_always_critical():
    for flag in ["ptosis", "breathing", "speech_swallow", "bleeding", "unconscious", "weakness", "vomiting_abdominal"]:
        f = Facts(snake=True, bite=True, red_flags=[flag])
        assert decide(f).level == "CRITICAL"


def test_monotone_more_care_never_less():
    """Adding any fact to a snakebite never lowers the level and never removes go_hospital."""
    rank = {"POSSIBLE": 1, "URGENT": 2, "CRITICAL": 3, "SUPPORT": 4}
    bool_keys = ["done_tourniquet", "done_cut", "done_healer", "done_ate", "done_walked", "child", "pregnant", "swelling"]
    base = decide(Facts(snake=True, bite=True))
    for combo in itertools.chain.from_iterable(itertools.combinations(bool_keys, r) for r in range(0, 4)):
        f = Facts(snake=True, bite=True)
        for k in combo:
            setattr(f, k, True)
        p = decide(f)
        assert rank[p.level] >= rank[base.level]
        assert not check_invariants(p)


def test_fuzz_invariants():
    rng = random.Random(7)
    words = ["saanp", "snake", "kaata", "bit", "rope", "ojha", "dog", "breath", "palak", "khoon", "floor", "woke",
             "vomit", "child", "pregnant", "no", "not", "hello", "prevent", "assam", "10 min", "behosh", "kutta"]
    for _ in range(3000):
        msg = " ".join(rng.choice(words) for _ in range(rng.randint(1, 8)))
        p = decide(parse(msg))
        assert not check_invariants(p), (msg, check_invariants(p))
        f = parse(msg)
        if f.snake and f.bite:
            assert p.level in ("URGENT", "CRITICAL", "SUPPORT"), msg


def test_15400_only_in_pilot_states():
    assert "call_15400" in decide(parse("snake bit me in assam")).item_ids()
    assert "call_15400" not in decide(parse("snake bit me in bihar")).item_ids()


def test_occult_krait():
    p = decide(parse("my son slept on the floor and woke up with drooping eyelids"))
    assert p.level == "CRITICAL" and "suspect_krait" in p.item_ids()


def test_followup_yes_escalates():
    p = decide(parse("snake bit my mother"), answered={"breathing": True})
    assert p.level == "CRITICAL"


def test_followup_no_cannot_unsay_symptom():
    p = decide(parse("snake bit him, he is bleeding from gums"), answered={"bleeding": False})
    assert p.level == "CRITICAL"


# ---------------------------------------------------------------- llm merge is monotone
def test_llm_merge_only_adds():
    base = parse("snake bit him, he is vomiting")
    merged, added = llm.merge(base, {"red_flags": [], "snake": False, "done_tourniquet": True, "other_animal": "dog"})
    assert merged.snake and "vomiting_abdominal" in merged.red_flags and merged.done_tourniquet
    assert merged.other_animal is None
    assert added == ["done_tourniquet"]


def test_llm_cannot_add_denied_flag():
    base = parse("snake bit him, no breathing problem")
    merged, _ = llm.merge(base, {"red_flags": ["breathing"]})
    assert "breathing" not in merged.red_flags


# ---------------------------------------------------------------- quiz bank
def test_quiz_each_question_one_correct_and_parallel():
    for c in quiz.ORDER:
        for form in "AB":
            opts = quiz.Q[(c, form)]["options"]
            assert sum(o[3] for o in opts) == 1, (c, form)
            assert not any(o[3] and o[4] for o in opts)
            assert len(opts) == 4


# ---------------------------------------------------------------- API
def _complete(headers=None, pre_right=False, post_right=True, lang="en", ip="testclient"):
    h = headers or {}
    client = TestClient(app, client=(ip, 50000))
    r = client.post("/api/learn/start", json={"lang": lang}, headers=h).json()
    sid, pre_form = r["session"], r["form"]
    ans = {q["concept"]: (quiz.correct_option(q["concept"], pre_form) if pre_right else
                          next(o["id"] for o in q["options"] if o["id"] != quiz.correct_option(q["concept"], pre_form)))
           for q in r["questions"]}
    r2 = client.post("/api/learn/pre", json={"session": sid, "answers": ans}, headers=h).json()
    post_form = r2["form"]
    ans2 = {q["concept"]: (quiz.correct_option(q["concept"], post_form) if post_right else
                           next(o["id"] for o in q["options"] if o["id"] != quiz.correct_option(q["concept"], post_form)))
            for q in r2["questions"]}
    r3 = client.post("/api/learn/post", json={"session": sid, "answers": ans2, "state": "Bihar", "role": "farmer"},
                     headers=h)
    return sid, r3


def test_learn_flow_and_impact_excludes_test():
    before = client.get("/api/impact").json()["learn"]["completed"]
    _, r = _complete(headers={"x-dansh-test": "1"})
    assert r.status_code == 200
    assert client.get("/api/impact").json()["learn"]["completed"] == before
    _, r = _complete(ip="10.0.0.1")
    j = r.json()
    assert j["post"]["correct"] == 6 and j["pre"]["correct"] == 0
    imp = client.get("/api/impact").json()["learn"]
    assert imp["completed"] == before + 1
    assert imp["per_concept"]["tourniquet"]["correct_post_pct"] is not None


def test_cannot_complete_twice_or_skip_pre():
    sid, r = _complete(ip="10.0.0.2")
    again = client.post("/api/learn/post", json={"session": sid, "answers": {}})
    assert again.status_code == 409
    s = client.post("/api/learn/start", json={"lang": "en"}).json()["session"]
    assert client.post("/api/learn/post", json={"session": s, "answers": {}}).status_code == 409


def test_device_cap():
    before = client.get("/api/impact").json()["learn"]["completed"]
    for _ in range(7):
        _complete(ip="10.9.9.9")
    after = client.get("/api/impact").json()["learn"]["completed"]
    assert after - before == 5


def test_consult_api_and_csv():
    r = client.post("/api/consult", json={"message": "saanp ne kaata, saans nahi aa rahi", "lang": "hi"},
                    headers={"x-dansh-test": "1"}).json()
    assert r["level"] == "CRITICAL" and r["calls"][0] == "108"
    assert "go_hospital" in r["item_ids"]
    csv = client.get("/api/impact/sessions.csv").text
    assert csv.splitlines()[0].startswith("completed_utc")
    assert "10.0.0" not in csv  # no IPs leak


def test_pages():
    for path in ["/", "/check", "/impact", "/static/app.js", "/api/health"]:
        assert client.get(path).status_code == 200, path


# ---------------------------------------------------------------- fixes for eval run 0 misses
def test_krait_with_no_bite_mark():
    p = decide(parse("my son slept on the floor and woke up at 4am vomiting, eyes half closed, no bite mark"))
    assert "suspect_krait" in p.item_ids() and p.level == "CRITICAL"


def test_sucked_blood_is_not_bleeding_sign():
    f = parse("saanp ne kaata, blade se cheera lagaya aur khoon choosa")
    assert "bleeding" not in f.red_flags and f.done_cut


def test_age_makes_child():
    assert parse("Snake bit my 6 year old daughter").child
    assert not parse("Snake bit my 40 year old father").child


def test_yesterday_is_late():  # held-out run 1 miss
    p = decide(parse("bitten by a snake yesterday, today she is vomiting blood"))
    assert "late_note" in p.item_ids()
