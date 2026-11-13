"""Deterministic protocol engine: facts -> plan.

The rules below decide everything that matters: the urgency level, which steps,
in which order, and which warnings. They follow the MoHFW Standard Treatment
Guidelines (2017). Rules only ever move toward MORE care: no input can produce
"stay home" or "wait and see" for a possible snakebite.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .content import FOLLOW_UPS, HELPLINE_15400_STATES, ITEMS, RED_FLAGS, UI, cite, text
from .parser import Facts

LEVELS = ["OFF_TOPIC", "OTHER", "INFO", "POSSIBLE", "URGENT", "CRITICAL", "SUPPORT"]
LOOKALIKE = {"rat", "lizard", "insect"}  # animals a hidden krait bite is commonly blamed on
NEVER_SAY_FOR_BITES = {"dont_tourniquet", "dont_cut_suck", "dont_healer"}  # always included for any bite


@dataclass
class Plan:
    level: str
    title: str
    do: list[dict] = field(default_factory=list)
    dont: list[dict] = field(default_factory=list)
    fixes: list[dict] = field(default_factory=list)
    notes: list[dict] = field(default_factory=list)
    understood: list[str] = field(default_factory=list)
    ask: list[dict] = field(default_factory=list)
    show_hospitals: bool = False
    calls: list[str] = field(default_factory=list)
    rule_trace: list[str] = field(default_factory=list)
    lang: str = "en"

    def item_ids(self) -> list[str]:
        return [i["id"] for i in self.do + self.dont + self.fixes + self.notes]

    def to_dict(self) -> dict:
        return {
            "level": self.level, "title": self.title, "do": self.do, "dont": self.dont, "fixes": self.fixes,
            "notes": self.notes, "understood": self.understood, "ask": self.ask,
            "show_hospitals": self.show_hospitals, "calls": self.calls, "rule_trace": self.rule_trace,
            "lang": self.lang, "item_ids": self.item_ids(),
        }


def _item(item_id: str, lang: str) -> dict:
    return {"id": item_id, "text": text(item_id, lang), "source": cite(item_id)}


def decide(f: Facts, lang: str | None = None, answered: dict | None = None) -> Plan:
    """answered: {flag: True/False} from the follow-up yes/no buttons."""
    lang = lang or f.lang or "en"
    answered = answered or {}
    flags = list(dict.fromkeys(f.red_flags))
    for k, v in answered.items():
        if k in RED_FLAGS and v and k not in flags:
            flags.append(k)
    denied = set(f.negated) | {k for k, v in answered.items() if v is False}
    flags = [x for x in flags if x not in denied or x in f.red_flags]  # a stated symptom is never un-said

    trace: list[str] = []
    is_bite_context = f.snake or f.unknown_bite or f.occult_krait or (f.bite and not f.other_animal)

    # R0 safety: self-harm language always surfaces crisis lines first.
    if f.self_harm:
        trace.append("R0 self-harm language -> crisis lines")
        p = Plan("SUPPORT", UI["level_SUPPORT"][lang], lang=lang, rule_trace=trace, calls=["14416", "112"])
        p.notes.append(_item("self_harm", lang))
        if not is_bite_context:
            return p
        # fall through: a bite is still an emergency; keep the crisis line on top.
        trace.append("R0b bite also present -> continue with bite protocol")

    neuro = set(flags) & {"ptosis", "speech_swallow", "breathing", "weakness"}
    strong_neuro = set(flags) & {"ptosis", "speech_swallow"}
    if f.other_animal in LOOKALIKE and flags and not f.occult_krait:
        # "rat bit him at night, now vomiting": a krait bite is often blamed on a rat
        f.occult_krait = bool(f.night_floor or strong_neuro)
        f.unknown_bite = True
        is_bite_context = True
        trace.append(f"R1d danger signs {flags} after a '{f.other_animal}' bite -> treat as possible snakebite")
    elif f.other_animal in LOOKALIKE and f.night_floor and not f.occult_krait:
        # "a rat bit my son at night while he slept on the floor": the classic hidden krait bite
        f.unknown_bite = True
        is_bite_context = True
        trace.append(f"R1f '{f.other_animal}' bite at night / on the floor -> treat as possible snakebite")
    elif f.other_animal and (set(flags) - {"bleeding"} or f.systemic) and not f.occult_krait:
        # any body-wide danger sign after an animal bite: the animal may be wrong, the signs are not
        f.unknown_bite = True
        is_bite_context = True
        trace.append(f"R1e danger signs {sorted(set(flags) - {'bleeding'}) or ['systemic']} although "
                     f"'{f.other_animal}' named -> snakebite protocol")
    # R1 another animal named, no snake, no doubt about it -> out of scope with a safe pointer.
    if f.other_animal and not f.snake and not f.unknown_bite and not f.occult_krait:
        trace.append(f"R1 other animal ({f.other_animal}) -> out of scope")
        p = Plan("OTHER", UI["level_OTHER"][lang], lang=lang, rule_trace=trace, calls=["108", "112"])
        if flags:
            p.understood = [RED_FLAGS[k][lang] for k in flags]
            trace.append(f"R1b danger signs {flags} with another animal -> 108 first")
        p.notes.append(_item("other_bite", lang))
        return p
    if f.other_animal and f.unknown_bite and not f.snake:
        trace.append(f"R1c animal ({f.other_animal}) named but uncertain -> treat as possible snakebite")

    # R2 prevention / general question / snake mentioned with nothing happening -> prevention advice.
    general = (f.prevention or (f.generic_question and f.snake) or f.snake_mention_only)
    if general and not (f.bite or f.unknown_bite or f.occult_krait or flags or f.swelling or f.contact):
        trace.append("R2 prevention question -> prevention advice")
        p = Plan("INFO", UI["level_INFO"][lang], lang=lang, rule_trace=trace, calls=["108"])
        for i in ("prevent_torch", "prevent_sleep", "prevent_hands"):
            p.do.append(_item(i, lang))
        return p

    # R3 nothing recognisable -> ask the user to describe what happened.
    if not is_bite_context:
        if set(flags) & {"ptosis", "speech_swallow"}:  # krait-type neuro signs without a stated cause
            trace.append("R3b symptoms without a stated cause -> possible snakebite (krait can be painless)")
            is_bite_context = True
            f.occult_krait = True
        else:
            trace.append("R3 no snake/bite recognised -> ask")
            p = Plan("OFF_TOPIC", UI["level_OFF_TOPIC"][lang], lang=lang, rule_trace=trace, calls=["112", "108"])
            p.notes.append(_item("off_topic", lang))
            return p

    # From here on: a (possible) snakebite. Every path sends the person to hospital.
    if flags:
        level = "CRITICAL"
        trace.append(f"R4 danger signs {flags} -> CRITICAL")
    elif f.systemic:
        level = "CRITICAL"
        trace.append("R4b a body-wide change after the bite (not a listed sign) -> CRITICAL")
    elif f.snake:
        level = "URGENT"
        trace.append("R5 snake named, no danger signs yet -> URGENT")
    else:
        level = "POSSIBLE"
        trace.append("R6 unknown bite / suspected krait -> POSSIBLE (treated as snakebite)")
    if f.self_harm:
        level_title = UI[f"level_{level}"][lang]
        p = Plan("SUPPORT", level_title, lang=lang, rule_trace=trace, calls=["108", "14416", "112"])
        p.notes.append(_item("self_harm", lang))
        p.rule_trace.append(f"R0c bite level would be {level}")
    else:
        p = Plan(level, UI[f"level_{level}"][lang], lang=lang, rule_trace=trace)

    p.show_hospitals = True
    p.understood = [RED_FLAGS[k][lang] for k in flags]

    if level == "CRITICAL":
        p.notes.insert(0, _item("critical_signs", lang))
    if f.occult_krait:
        p.notes.append(_item("suspect_krait", lang))
        trace.append("R7 night/floor + symptoms, no bite seen -> suspect krait")
    if not f.snake and f.unknown_bite:
        p.notes.append(_item("unsure_treat_as_snake", lang))
    if f.child:
        p.notes.append(_item("child_note", lang))
    if f.pregnant:
        p.notes.append(_item("pregnant_note", lang))
    if f.minutes_since is not None and f.minutes_since >= 360:
        p.notes.append(_item("late_note", lang))
        trace.append("R8 >6 h since bite -> antivenom can still help")

    # Ordered DO list. Calls first, then the person, then the journey.
    order = ["call_108"]
    if f.state and f.state in HELPLINE_15400_STATES:
        order.append("call_15400")
        trace.append(f"R9 state {f.state} in 15400 pilot -> add helpline")
    order.append("go_hospital")
    if "unconscious" in flags or "vomiting_abdominal" in flags or "breathing" in flags:
        order.append("recovery_position")
    order += ["reassure", "immobilise", "no_walk", "remove_tight", "nil_by_mouth", "note_time", "stay_24h"]
    p.do = [_item(i, lang) for i in order]
    p.calls = (["108"] + (["15400"] if "call_15400" in order else []) + ["112"]) if not f.self_harm else p.calls

    # Corrections for what was already done (shown above the DON'T list).
    for key, fix in (("done_tourniquet", "fix_tourniquet"), ("done_cut", "fix_cut"), ("done_healer", "fix_healer"),
                     ("done_ate", "fix_ate"), ("done_walked", "fix_walked")):
        if getattr(f, key):
            p.fixes.append(_item(fix, lang))
            trace.append(f"R10 {key} -> {fix}")

    dont = ["dont_tourniquet", "dont_cut_suck", "dont_healer", "dont_catch"]
    p.dont = [_item(i, lang) for i in dont]

    # Follow-up questions for danger signs we do not know about yet.
    for key, q in FOLLOW_UPS:
        if key not in flags and key not in denied:
            p.ask.append({"flag": key, "q": q[lang]})
    return p


def check_invariants(p: Plan) -> list[str]:
    """Safety invariants the eval and tests assert on every plan."""
    errs = []
    ids = set(p.item_ids())
    if p.level in ("POSSIBLE", "URGENT", "CRITICAL"):
        if "go_hospital" not in ids:
            errs.append("bite plan without go_hospital")
        if "call_108" not in ids:
            errs.append("bite plan without call_108")
        missing = NEVER_SAY_FOR_BITES - ids
        if missing:
            errs.append(f"bite plan missing warnings {sorted(missing)}")
    for i in ids:
        if i not in ITEMS:
            errs.append(f"unknown item {i}")
    return errs
