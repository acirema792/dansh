"""Second verifier pass (verify-r1b). Every input below must reach a hospital level.
Over-triage is acceptable; a false safe is not."""
import os
import tempfile

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "v1b.db"))

import pytest  # noqa: E402

from app.parser import parse  # noqa: E402
from app.protocol import decide  # noqa: E402

BITE = {"POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"}

MUST_GO_TO_HOSPITAL = [
    # doubt about the animal
    "maybe a rat bit him in the field, it was dark",
    "maybe a dog bit him",
    "I think a dog bit me but it was dark and I didn't see",
    "I think a rat bit my daughter in the field",
    "shayad kutte ne kaata, andhere mein dikha nahi",
    "rat ne kaata shayad, pakka nahi pata",
    "rat or something bit my son at night",
    "pata nahi kisne kaata, bichhu ya kuch aur",
    "pata nahi kisne kaata, chuha ho sakta hai",
    "शायद चूहे ने काटा, रात को",
    "cat bit? not sure, it was dark, two small holes",
    "kutte ne kaata ya kuch aur pata nahi, do daant ke nishaan",
    "i think a scorpion stung me but i did not see it, it was dark",
    "not sure if a dog bit him or something else",
    "rat bite i guess, now his eyes are closing",
    # thorn-like descriptions
    "pair me sui jaisa kuch chubha khet me, ab jalan ho rahi hai",
    "felt a needle-like prick on my foot while walking at night",
    "nail jaisa kuch chubha, do nishaan hai",
    "two holes on his foot, maybe a thorn",
    "was it a thorn? two marks and the leg is swelling",
    "something pricked my child in the field, maybe a thorn, now he is crying a lot",
    "kuch chubha, kaanta ya kuch aur pata nahi, raat ko khet me",
    # attack words
    "snake attack in the field just now, how to protect the leg",
    "snake strike on the hand, how to protect it",
    "krait attack at night, how to protect",
    "snake attack! how to protect, help fast",
    "cobra attack, help, protect",
    "saanp ka hamla, help, bachav karo",
    "saanp hamla, bachav, help",
    "साँप का हमला, बचाव करो",
    # snake near a person
    "a snake came near my father, he is shouting, keep out",
    "snake entered the house and my child is near it, how to keep out",
    # previously open
    "something long slid over my foot in the paddy field and now there are two red dots",
    "stepped on something in the grass at night, felt like glass, now swelling",
    "two puncture wounds on her ankle after walking in the field",
]


@pytest.mark.parametrize("msg", MUST_GO_TO_HOSPITAL)
def test_r1b_never_false_safe(msg):
    p = decide(parse(msg))
    assert p.level in BITE and "go_hospital" in p.item_ids(), (msg, p.level, p.rule_trace)


@pytest.mark.parametrize("msg", ["snake bit him, he is drooling", "snake bit him and now he is drooling and can't talk"])
def test_r1b_drooling_after_bite_is_danger(msg):
    assert decide(parse(msg)).level == "CRITICAL", msg


@pytest.mark.parametrize("msg,level", [
    ("seeing two snakes in the yard", "URGENT"),     # must not be CRITICAL from "seeing two"
    ("my baby is drooling, teething", "OFF_TOPIC"),
    ("I pricked my finger while sewing", "OFF_TOPIC"),
    ("kutte ne kaata, kuch karo", "OTHER"),
    ("a dog bit my son, maybe rabies?", "OTHER"),
    ("monkey bit me, not sure what to do", "OTHER"),
    ("cat scratched me, maybe infection", "OTHER"),
])
def test_r1b_over_alarm_controls(msg, level):
    assert decide(parse(msg)).level == level, (msg, decide(parse(msg)).rule_trace)
