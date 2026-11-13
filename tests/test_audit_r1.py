"""Regression tests for audit round 1 findings (inputs copied from loop/audits/round-1.md)."""
import os
import tempfile

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "r1.db"))

import pytest  # noqa: E402

from app.parser import parse  # noqa: E402
from app.protocol import decide  # noqa: E402

BITE_LEVELS = {"POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"}


# F1: danger signs must survive Hindi/English phrasings that look like negations
@pytest.mark.parametrize("msg,flag", [
    ("saanp ne kaata, koi madad karo saans nahi aa rahi", "breathing"),
    ("साँप ने काटा, कोई मदद करो सांस नहीं आ रही", "breathing"),
    ("saanp ne kaata, saans theek nahi hai", "breathing"),
    ("साँप ने काटा, सांस ठीक नहीं है", "breathing"),
    ("snake bit him, breathing not fine", "breathing"),
    ("snake bit him, breathing fast, not fine", "breathing"),
    ("saanp ne kaata, kamzori theek nahi ho rahi", "weakness"),
    ("snake bit him, no idea why breathing is hard", "breathing"),
    ("saanp ne kaata, khoon nahi ruk raha", "bleeding"),
    ("saanp ne kaata, khoon band nahi ho raha", "bleeding"),
    ("saanp ne kaata, ulti nahi ruk rahi", "vomiting_abdominal"),
    ("snake bite, vomiting nahi ruk rahi", "vomiting_abdominal"),
])
def test_f1_flag_kept(msg, flag):
    f = parse(msg)
    assert flag in f.red_flags, (msg, f.red_flags, f.negated)
    assert decide(f).level == "CRITICAL"


# F2/F3/F8: real or possible bites must enter the snakebite protocol
@pytest.mark.parametrize("msg", [
    "a snake got my son, how do I protect him",
    "snake attack on my son, how to protect him now",
    "saanp ne hamla kiya, bachav kaise kare",
    "fang marks",
    "my child was playing near the woodpile and now has fang marks",
    "my husband can't open his eyes and is drooling, slept outside",
    "snakbite",
    "snakebit on the leg",
    "mere pair me kuch chubh gaya, khet me",
    "while chasing a rat, I was bitten on the hand in the dark",
    "bitten while cleaning the cowshed, maybe a rat",
    "dog barked at something, then my son screamed, two marks on leg",
])
def test_f2_f3_f8_bites_enter_protocol(msg):
    p = decide(parse(msg))
    assert p.level in BITE_LEVELS, (msg, p.level, p.rule_trace)
    assert "go_hospital" in p.item_ids()


# Controls that must stay out of the protocol
@pytest.mark.parametrize("msg,level", [
    ("How can I protect my family from snakes during the monsoon?", "INFO"),
    ("dog bit me", "OTHER"),
    ("bichhu ne kaata", "OTHER"),
    ("hello", "OFF_TOPIC"),
    ("my child has a fever and cough, maybe flu", "OFF_TOPIC"),
    ("kuch samajh nahi aa raha", "OFF_TOPIC"),
])
def test_controls_unchanged(msg, level):
    assert decide(parse(msg)).level == level


# Denials that must still be honoured
@pytest.mark.parametrize("msg,flag", [
    ("snake bite, no bleeding", "bleeding"),
    ("saanp ne kaata, khoon nahi aa raha", "bleeding"),
    ("snake bite, breathing is normal", "breathing"),
    ("saanp ne kaata, saans theek hai", "breathing"),
    ("snake bit him, no difficulty breathing", "breathing"),
])
def test_denials_still_work(msg, flag):
    assert flag not in parse(msg).red_flags


def test_info_and_other_always_offer_108():
    assert "108" in decide(parse("how to prevent snakebite")).calls
    assert decide(parse("a bee stung my son, now he is breathless")).calls[0] == "108"


def test_fuzz_snake_plus_bite_word_never_out_of_protocol():
    import random
    rng = random.Random(11)
    snake = ["snake", "saanp", "साँप", "cobra", "naag", "krait"]
    # "attack"/"hamla" alone are generic ("protect from snake attack"); they count as a bite with a person
    # or in the past tense (see test_verify_r1 V4). Changed after verifier round 1 - logged in loop/STATE.md.
    bite = ["bit", "bitten", "kaata", "काटा", "attacked my", "hamla kiya", "fang marks", "dasa"]
    filler = ["my", "son", "how", "protect", "prevent", "help", "no", "not", "dog", "rat", "maybe", "kya", "karein", "bachav"]
    for _ in range(2000):
        words = [rng.choice(snake), rng.choice(bite)] + [rng.choice(filler) for _ in range(rng.randint(0, 6))]
        rng.shuffle(words)
        msg = " ".join(words)
        assert decide(parse(msg)).level in BITE_LEVELS, msg
