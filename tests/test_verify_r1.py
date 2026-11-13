"""Regression tests for the round-1 verifier's rejections (inputs copied from its report)."""
import os
import tempfile

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "v1.db"))

import pytest  # noqa: E402

from app.parser import parse  # noqa: E402
from app.protocol import decide  # noqa: E402

BITE = {"POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"}


# V1: explicit other-animal bites must keep the animal-bite answer even with doubt words
@pytest.mark.parametrize("msg", [
    "kutte ne kaata, kuch karo",
    "a dog bit my son, maybe rabies?",
    "monkey bit me, not sure what to do",
    "bichhu ne kaata, kuch karo",
    "a bee stung me, maybe allergic?",
    "cat bit my daughter, not sure if serious",
    "dog bit me",
])
def test_v1_explicit_other_animal_stays_other(msg):
    p = decide(parse(msg))
    assert p.level == "OTHER", (msg, p.level, p.rule_trace)
    assert "other_bite" in p.item_ids()


# ...but a genuinely uncertain animal still enters the snakebite protocol
@pytest.mark.parametrize("msg", [
    "bitten while cleaning the cowshed, maybe a rat",
    "dog barked at something, then my son screamed, two marks on leg",
    "while chasing a rat, I was bitten on the hand in the dark",
    "a rat bit my son while sleeping on the floor, now he can't open his eyes",
])
def test_v1_uncertain_animal_is_possible_snakebite(msg):
    p = decide(parse(msg))
    assert p.level in BITE and "go_hospital" in p.item_ids(), (msg, p.level, p.rule_trace)


# V2: uncertain bite + prevention words must still get the hospital plan
@pytest.mark.parametrize("msg", [
    "pair me kuch chubh gaya, kaise bachav kare",
    "two marks on his leg, how to protect him",
    "बेटे को कुछ चुभ गया, बचाव कैसे करें",
])
def test_v2_uncertain_bite_with_prevention_words(msg):
    assert decide(parse(msg)).level in BITE, msg


# V3: danger signs that were still dropped
@pytest.mark.parametrize("msg,flag", [
    ("saanp ne kaata, khoon nahi jam raha", "bleeding"),
    ("saanp ne kaata, khoon nahi rok pa rahe", "bleeding"),
    ("saanp ne kaata, khoon nahi thahar raha", "bleeding"),
    ("saanp ne kaata, ulti nahi thahar rahi", "vomiting_abdominal"),
    ("snake bite no ambulance bleeding a lot", "bleeding"),
    ("snake bit him, breathing is ok for now but getting worse", "breathing"),
])
def test_v3_flags_kept(msg, flag):
    f = parse(msg)
    assert flag in f.red_flags, (msg, f.red_flags, f.negated)


# V4: false alarms
@pytest.mark.parametrize("msg,level", [
    ("how to protect from snake attack in the fields", "INFO"),
    ("why do snakes strike", "INFO"),
    ("fever and vomiting, he slept badly", "OFF_TOPIC"),
    ("my baby is drooling, teething", "OFF_TOPIC"),
    ("kaanta chubh gaya pair me", "OFF_TOPIC"),
    ("a thorn pricked my finger", "OFF_TOPIC"),
])
def test_v4_false_alarms(msg, level):
    p = decide(parse(msg))
    assert p.level == level, (msg, p.level, p.rule_trace)


def test_snake_seen_with_person_still_urgent():
    assert decide(parse("snake! my father!")).level in BITE
    assert decide(parse("saanp ne papa ko")).level in BITE


# Fixed AFTER held-out set 2 run 1 (eval_results/live-holdout2-run1.md); the held-out score stays as recorded.
def test_h2_double_vision_is_danger_sign():
    assert decide(parse("bitten by a krait last night, now he says he sees double")).level == "CRITICAL"


def test_h2_keep_snakes_out_is_prevention():
    assert decide(parse("what should I do to keep snakes out of my house?")).level == "INFO"
