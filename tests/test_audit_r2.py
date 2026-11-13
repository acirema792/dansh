"""Audit round 2 (loop/audits/round-2.md) - classes 1-8. Inputs copied from the report."""
import os
import tempfile

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "r2.db"))

import pytest  # noqa: E402

from app.parser import Facts, parse  # noqa: E402
from app.protocol import decide  # noqa: E402

BITE = {"POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"}


@pytest.mark.parametrize("msg", [  # class 1, 4, 5, 6, 8: must reach hospital
    "a snake was near my son and now his leg is swollen, how do we protect him",
    "snake in the house, my daughter is crying and her hand has two small wounds, how to keep snakes out",
    "सांप घर में था, बेटे के पैर पर दो घाव हैं, बचाव कैसे करें",
    "saanp ke paas khel raha tha beta, ab pair suj gaya, bachav kaise karein",
    "saanp ghar me ghus gaya, beti ke pair me dard hai, bachav kaise kare",
    "how to protect my son, a snake touched his foot",
    "papa ki aankhen nahi khul rahi subah se",
    "bacche ki palke gir rahi hai, raat ko zameen par soya tha",
    "felt like a needle prick in the field at night, now swelling",
    "pair me sui jaisa chubha khet me, ab sujan aur chakkar",
    "kuch chubh gaya, keel jaisa laga, ab pair sooj raha aur ulti ho rahi",
    "a rat bit my son, now his eyelids are drooping",
    "we think a rat bit grandpa, he is vomiting and cannot swallow",
    "I thought it was a rat but it was long and black and it bit my son",
    "was it a scorpion? my son was bitten in the field and is drowsy",
    "🐍🐍 help my son",
    "साप चावला",
])
def test_r2_reaches_hospital(msg):
    p = decide(parse(msg))
    assert p.level in BITE and "go_hospital" in p.item_ids(), (msg, p.level, p.rule_trace)


@pytest.mark.parametrize("msg", [  # class 2
    "snake bite no breathing",
    "saanp ne kaata, no breathing, help",
    "snake bit him, is his breathing ok? it sounds strange",
])
def test_r2_no_breathing_is_critical(msg):
    f = parse(msg)
    assert "breathing" in f.red_flags and "breathing" not in f.negated, (msg, f.red_flags, f.negated)


def test_r2_breathing_question_not_denial():
    f = parse("snake bit him, how do I know if his breathing is ok")
    assert "breathing" not in f.negated


@pytest.mark.parametrize("msg,flag", [  # class 3
    ("snake bit him and he collapsed", "unconscious"),
    ("saanp ne kaata, woh passed out ho gaya", "unconscious"),
    ("snake bite, he is having fits", "unconscious"),
    ("saanp ne kaata, jhatke aa rahe hai", "unconscious"),
    ("snake bite, convulsions", "unconscious"),
    ("snake bit him, he is gasping", "breathing"),
    ("saanp ne kaata, haanf raha hai", "breathing"),
    ("snake bite, lips turning blue", "breathing"),
    ("saanp ne kaata, gala band ho raha", "speech_swallow"),
    ("snake bite, hosh me nahi hai", "unconscious"),
    ("snake bit him, he can't hold his head up", "weakness"),
    ("saanp ne kaata, gardan latak rahi", "weakness"),
    ("snake bite, no strength in his body", "weakness"),
    ("snake bite, eyes not opening", "ptosis"),
    ("saanp ne kaata, aankh nahi khul rahi", "ptosis"),
    ("saanp ne kaata, peshab laal hai", "bleeding"),
    ("snake bite, urine is red", "bleeding"),
    ("snake bite, chest tight", "breathing"),
    ("saanp ne kaata, neend aa rahi hai bahut", "unconscious"),
    ("snake bit him, he is very sleepy", "unconscious"),
])
def test_r2_vocab(msg, flag):
    f = parse(msg)
    assert flag in f.red_flags, (msg, f.red_flags)
    assert decide(f).level == "CRITICAL"


@pytest.mark.parametrize("msg", ["main marna chahta hoon, saanp ne kaata", "mujhe jeena nahi hai"])
def test_r2_hinglish_self_harm(msg):
    p = decide(parse(msg))
    assert "self_harm" in p.item_ids()


def test_r2_support_keeps_108_first_with_bite():
    p = decide(parse("a snake bit me, I want to end my life anyway"))
    assert p.calls[0] == "108" and "14416" in p.calls


@pytest.mark.parametrize("msg,level", [  # false alarms
    ("my baby bit my finger", "OFF_TOPIC"),
    ("I bit my tongue while eating", "OFF_TOPIC"),
    ("teeth marks from my toddler biting my arm", "OFF_TOPIC"),
    ("my son fell and has two marks on his knee from the stairs", "OFF_TOPIC"),
    ("what should I keep at home for snakebite first aid", "INFO"),
    ("is there a snake helpline in Bihar", "INFO"),
])
def test_r2_false_alarms(msg, level):
    p = decide(parse(msg))
    assert p.level == level, (msg, p.level, p.rule_trace)


def test_r2_llm_cannot_demote_bite_to_support_order():
    f = Facts(snake=True, bite=True, self_harm=True)
    assert decide(f).calls[0] == "108"
