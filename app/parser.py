"""Keyword parser: free text (English, Hindi in Devanagari, Hinglish) -> facts.

Deterministic and offline. The optional LLM parser (llm.py) can only ADD facts on
top of this one, never remove a danger sign this parser found.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field

from .content import RED_FLAGS


@dataclass
class Facts:
    snake: bool = False            # a snake is mentioned as the cause
    bite: bool = False             # a bite/sting is mentioned
    unknown_bite: bool = False     # "something bit" without naming the animal
    other_animal: str | None = None
    occult_krait: bool = False     # night/floor + symptoms with no bite seen
    prevention: bool = False       # asking how to stay safe
    self_harm: bool = False
    red_flags: list[str] = field(default_factory=list)
    swelling: bool = False
    done_tourniquet: bool = False
    done_cut: bool = False
    done_healer: bool = False
    done_ate: bool = False
    done_walked: bool = False
    done_catch: bool = False
    child: bool = False
    pregnant: bool = False
    minutes_since: int | None = None
    state: str | None = None
    lang: str = "en"
    negated: list[str] = field(default_factory=list)  # red flags explicitly denied
    generic_question: bool = False  # "why do snakes strike" with no person involved
    night_floor: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    s = s.replace("ँ", "ं")  # candrabindu -> anusvara: साँप == सांप
    return re.sub(r"\s+", " ", s).strip()


def _any(text: str, words: list[str]) -> bool:
    for w in words:
        if DEVANAGARI.search(w):
            if _norm(w) in text:
                return True
        elif re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", text):
            return True
    return False


SNAKE = ["snake", "snakes", "snakebite", "saanp", "saap", "sanp", "saamp", "samp", "saap ne", "naag", "nag ne",
         "cobra", "krait", "karait", "kraitt", "viper", "snakbite", "snakebit", "snek", "snak", "snakes bite", "russell", "russells", "ghonas", "sarp", "sarpdansh", "serpent",
         "साँप", "सांप", "सर्प", "नाग", "करैत", "कोबरा", "वाइपर", "घोणस", "सर्पदंश", "फन"]
BITE = ["bite", "bit", "bitten", "biting", "bites", "kaata", "kata", "kaat", "kaatа", "kaat liya", "kaat diya", "kat liya",
        "daswa", "dasa", "dans", "dansh", "dank", "sting", "stung", "attack", "attacked", "struck", "strike",
        "hamla", "got my", "got him", "got her", "fang", "fangs", "fang marks", "snakbite", "snakebit",
        "काटा", "काट", "डसा", "डस", "डंस", "दंश", "डंक"]
UNKNOWN = ["something bit", "something has bitten", "kuch ne kaata", "kuch kaat", "kisi ne kaata", "pata nahi kisne",
           "dont know what bit", "don't know what bit", "not sure what bit", "unknown bite", "insect", "keeda", "kida",
           "fang marks", "fang", "fangs", "two marks", "two holes", "two dots", "do nishan", "do nishaan", "chubh",
           "chubha", "chubh gaya", "pricked", "prick", "चुभ", "दो निशान",
           "कुछ ने काटा", "किसी ने काटा", "पता नहीं किसने", "कीड़े", "कीड़ा"]
OTHER = {
    "dog": ["dog", "kutta", "kutte", "kutiya", "कुत्ता", "कुत्ते"],
    "scorpion": ["scorpion", "bichhu", "bichu", "bicchu", "बिच्छू", "बिच्छु"],
    "monkey": ["monkey", "bandar", "बंदर"],
    "bee": ["bee", "bees", "wasp", "honeybee", "madhumakhi", "tatayya", "ततैया", "मधुमक्खी"],
    "rat": ["rat", "chuha", "chooha", "चूहा", "चूहे"],
    "cat": ["cat", "billi", "बिल्ली"],
}
# Doubt words only count together with a bite word or a named animal ("maybe a rat bit me").
HEDGE = ["in the dark", "andhere", "andhere mein", "something", "kuch", "maybe", "shayad", "not sure", "pata nahi",
         "may have been", "might be", "i think", "lagta hai", "अंधेरे", "शायद", "पता नहीं", "कुछ"]
PREVENT = ["prevent", "prevention", "avoid", "stay safe", "keep away", "protect", "bachav", "bachaav", "kaise bache",
           "kaise bachein", "how to be safe", "बचाव", "बचें", "बचे", "रोकथाम"]
SELF_HARM = ["suicide", "kill myself", "end my life", "self harm", "self-harm", "want to die", "aatmahatya",
             "आत्महत्या", "मरना चाहता", "मरना चाहती"]

FLAG_WORDS = {
    "ptosis": ["droop", "drooping", "droopy", "eyelid", "eyelids", "ptosis", "double vision", "blurred vision",
               "blurry", "can't open eyes", "cannot open eyes", "cant open eyes", "eyes closing", "eyes are closing",
               "aankh band", "aankhen band", "aankhein band", "ankh band", "open his eyes", "open her eyes",
               "open their eyes", "open my eyes", "eyes heavy", "keep eyes open", "keep his eyes open", "palak", "palken", "dhundhla", "do do dikh",
               "पलक", "पलकें", "आंख बंद", "आंखें बंद", "धुंधला", "दो दो दिख", "आंखें नहीं खुल", "आंख नहीं खुल"],
    "breathing": ["breath", "breathe", "breathing", "breathless", "short of breath", "choking", "saans", "sans",
                  "saas", "dam ghut", "dum ghut", "सांस", "दम घुट", "श्वास"],
    "speech_swallow": ["slurred", "can't speak", "cannot speak", "cant speak", "can't swallow", "cannot swallow",
                       "difficulty swallowing", "trouble swallowing", "unable to swallow",
                       "slurring", "lar tapak", "laar", "trouble speaking", "bol nahi", "bol nhi",
                       "nigal nahi", "nigalne", "awaaz", "आवाज़", "बोल नहीं", "निगल", "बोलने में"],
    "bleeding": ["bleeding", "bleed", "blood", "khoon", "khun", "gums", "nosebleed", "nose bleed", "red urine",
                 "dark urine", "black urine", "brown urine", "naak se", "masood", "खून", "मसूड़", "नाक से", "लाल पेशाब",
                 "काला पेशाब", "रक्त"],
    "unconscious": ["unconscious", "fainted", "fainting", "faint", "drowsy", "not responding", "unresponsive",
                    "not waking", "won't wake", "hard to wake", "behosh", "behoshi", "hosh nahi", "sust",
                    "बेहोश", "होश नहीं", "सुस्त", "बेसुध"],
    "weakness": ["weak", "weakness", "paralysis", "paralysed", "paralyzed", "can't move", "cannot move",
                 "can't stand", "cannot stand", "limp", "kamzori", "kamjori", "lakwa", "lakva", "kamzor",
                 "कमज़ोरी", "कमजोरी", "कमज़ोर", "कमजोर", "लकवा", "हिल नहीं"],
    "vomiting_abdominal": ["vomit", "vomiting", "vomited", "throwing up", "stomach pain", "abdominal pain",
                           "belly pain", "stomach ache", "ulti", "ultee", "pet dard", "pet me dard", "pet mein dard",
                           "उल्टी", "पेट दर्द", "पेट में दर्द"],
}
SWELLING = ["swelling", "swollen", "swell", "sujan", "soojan", "sooj", "fool gaya", "phool gaya", "सूजन", "सूज", "फूल गया"]
DONE = {
    "done_tourniquet": ["tourniquet", "tied", "tie a", "tying", "rope", "string", "thread", "ligature", "band tied",
                        "tied tight", "tightly", "baandh", "bandh diya", "bandha", "bandhi", "baandha", "rassi",
                        "dori", "dhaga", "kas ke", "kaske", "बांध", "बांधा", "बांधी", "रस्सी", "धागा", "डोरी", "कसकर"],
    "done_cut": ["cut it", "cut the", "cut open", "made a cut", "blade", "knife", "razor", "sucked", "suck", "sucking",
                 "cheera", "chira", "choos", "choosa", "chusa", "चीरा", "चूस", "ब्लेड", "चाकू"],
    "done_healer": ["ojha", "ojhaa", "jhaad", "jhad", "jhaar", "jhar phook", "jhaad phoonk", "phoonk", "tantrik",
                    "bhagat", "vaid", "vaidya", "healer", "baba", "mantra", "temple", "mandir", "herb", "herbs",
                    "jadi", "jadi buti", "jaddi", "black stone", "snake stone", "patthar", "lep", "paste", "turmeric",
                    "haldi", "ओझा", "झाड़", "फूंक", "तांत्रिक", "भगत", "वैद्य", "बाबा", "मंत्र", "मंदिर", "जड़ी",
                    "पत्थर", "लेप", "हल्दी"],
    "done_ate": ["alcohol", "daaru", "daru", "sharab", "liquor", "gave him water", "gave her water", "gave water",
                 "gave milk", "drank", "ate", "aspirin", "painkiller", "ibuprofen", "combiflam", "khilaya", "pilaya",
                 "दारू", "शराब", "पिलाया", "खिलाया", "दवा दी"],
    "done_walked": ["walked", "walking", "ran", "running", "drove", "driving", "cycled", "chal ke", "chalke",
                    "chal kar", "paidal", "daud", "पैदल", "चलकर", "चल के", "दौड़"],
    "done_catch": ["killed the snake", "kill the snake", "caught the snake", "catch the snake", "catching",
                   "maar diya", "mar diya", "maar dala", "pakad", "pakda", "पकड़", "मार दिया", "मार डाला"],
}
CHILD = ["child", "kid", "baby", "toddler", "boy", "girl", "infant", "bachcha", "bacha", "bachche", "bachchi",
         "bacchi", "beta", "beti", "munna", "munni", "बच्चा", "बच्चे", "बच्ची", "बेटा", "बेटी", "मुन्ना"]
PREGNANT = ["pregnant", "pregnancy", "garbhvati", "garbhavati", "pet se", "गर्भवती", "पेट से"]
NIGHT_FLOOR = ["slept outside", "sleeping outside", "slept on the floor", "sleeping on the floor", "on the floor", "floor", "woke up", "woke", "at night",
               "in the morning", "early morning", "zameen par", "jameen par", "zamin", "neend", "subah", "raat",
               "ज़मीन", "जमीन", "सुबह", "रात", "नींद", "सो रहा", "सोया", "सोई"]

STATES = {
    "andhra pradesh": ["andhra pradesh", "andhra", "आंध्र प्रदेश"], "arunachal pradesh": ["arunachal"],
    "assam": ["assam", "असम"], "bihar": ["bihar", "बिहार"], "chhattisgarh": ["chhattisgarh", "छत्तीसगढ़"],
    "goa": ["goa"], "gujarat": ["gujarat", "गुजरात"], "haryana": ["haryana", "हरियाणा"],
    "himachal pradesh": ["himachal"], "jharkhand": ["jharkhand", "झारखंड"], "karnataka": ["karnataka", "कर्नाटक"],
    "kerala": ["kerala", "केरल"], "madhya pradesh": ["madhya pradesh", "मध्य प्रदेश", "mp me", "m.p."],
    "maharashtra": ["maharashtra", "महाराष्ट्र"], "manipur": ["manipur"], "meghalaya": ["meghalaya"],
    "mizoram": ["mizoram"], "nagaland": ["nagaland"], "odisha": ["odisha", "orissa", "ओडिशा"],
    "punjab": ["punjab", "पंजाब"], "rajasthan": ["rajasthan", "राजस्थान"], "sikkim": ["sikkim"],
    "tamil nadu": ["tamil nadu", "तमिलनाडु"], "telangana": ["telangana", "तेलंगाना"], "tripura": ["tripura"],
    "uttar pradesh": ["uttar pradesh", "उत्तर प्रदेश"], "uttarakhand": ["uttarakhand", "उत्तराखंड"],
    "west bengal": ["west bengal", "bengal", "पश्चिम बंगाल", "बंगाल"], "delhi": ["delhi", "दिल्ली"],
    "puducherry": ["puducherry", "pondicherry", "पुडुचेरी"], "jammu and kashmir": ["jammu", "kashmir"],
}
HINGLISH = ["ko", "ne", "hai", "tha", "thi", "kya", "kaise", "nahi", "abhi", "mere", "meri", "mera", "papa", "maa",
            "bhai", "behen", "pair", "haath", "kaata", "saanp", "ghante", "minute pehle", "pehle", "gaya", "gayi"]

TIME_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(min|mins|minute|minutes|मिनट|hr|hrs|hour|hours|ghanta|ghante|ghanto|घंटा|घंटे)")
WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "ten": 10, "half an": 0.5, "an": 1,
            "a": 1, "ek": 1, "do": 2, "teen": 3, "char": 4, "aadha": 0.5, "आधा": 0.5, "एक": 1, "दो": 2, "तीन": 3}
WORD_TIME_RE = re.compile(r"\b(one|two|three|four|five|six|ten|half an|an|a|ek|do|teen|char|aadha|आधा|एक|दो|तीन)\s+"
                          r"(min|minute|minutes|hour|hours|ghanta|ghante|मिनट|घंटा|घंटे)")
JUST_NOW = ["just now", "right now", "abhi abhi", "abhi-abhi", "अभी अभी", "अभी-अभी", "few minutes ago"]


def _detect_lang(raw: str, text: str) -> str:
    if DEVANAGARI.search(raw):
        return "hi"
    hits = sum(1 for w in HINGLISH if re.search(r"(?<![a-z])" + w + r"(?![a-z])", text))
    return "hi" if hits >= 2 else "en"


# Negation is handled conservatively: when unsure, the danger sign is KEPT.
# "not breathing", "can't open eyes", "saans nahi aa rahi" are symptoms, not denials, so plain
# "not"/"nahi" never negates an inability-type sign. Only explicit denials count.
# A denial must be adjacent ("no bleeding", "no difficulty breathing", "without swelling") and must not
# cross punctuation. "koi" is NOT a negator ("koi madad karo" = "someone help").
NEG_BEFORE = re.compile(r"(?:\bno\b|\bwithout\b|\bdenies\b|\bnever\b)\s+(?:(?:difficulty|trouble|problem|problems|"
                        r"sign|signs|issue|issues|sign of|signs of|active|visible)\s+)?$")
NORMAL_AFTER = re.compile(r"^\s*(?:is\s+|are\s+|hai\s+|है\s+)?(?:normal|normally|fine|ok|okay|theek|thik|ठीक|सामान्य)"
                          r"(?![^,.;!?।]{0,12}(?:\bnot\b|\bnahi\b|\bnahin\b|\bnhi\b|\bna\b|नहीं|नही))")
HI_NEG_AFTER = re.compile(r"^\s*(?:aa\s+|aa raha\s+|आ\s+)?(?:nahi|nahin|nhi|नहीं|नही)\b"
                          r"(?!\s*(?:ruk|ruka|rukta|rukti|rok|tham|tham\w*|thahar|thehar|jam|jamta|jam raha|band|"
                          r"रुक|रोक|थम|ठहर|जम|बंद))")
WORSENING = re.compile(r"\b(?:but|lekin|magar|par|worse|worsening|getting|badh|badhti|badh raha)\b|लेकिन|मगर|बढ़|बिगड़")
NEG_STOPPING = re.compile(r"(?:\bnot\b|\bnahi\b|नहीं)[^,.;!?।]{0,10}$")
PRESENCE_TYPE = {"bleeding", "vomiting_abdominal", "swelling"}  # "khoon nahi" = no bleeding


def _negated(text: str, words: list[str], flag: str = "") -> bool:
    """True only if EVERY mention of the sign is explicitly denied."""
    found = False
    for w in words:
        wn = _norm(w)
        pat = re.escape(wn) if DEVANAGARI.search(wn) else r"(?<![a-z])" + re.escape(wn) + r"(?![a-z])"
        for m in re.finditer(pat, text):
            found = True
            before = text[max(0, m.start() - 30): m.start()]
            after = text[m.end(): m.end() + 24]
            denied = bool(NEG_BEFORE.search(before)) or bool(NORMAL_AFTER.search(after))
            if denied and WORSENING.search(text[m.end(): m.end() + 40]):
                denied = False  # "breathing is ok for now but getting worse"
            if denied and NEG_STOPPING.search(before) and not NEG_BEFORE.search(before):
                denied = False
            if flag in PRESENCE_TYPE and HI_NEG_AFTER.search(after):
                denied = True
            if not denied:
                return False
    return found


YESTERDAY = ["yesterday", "last night", "kal raat", "kal shaam", "kal", "कल", "कल रात", "पिछली रात"]


def _minutes(text: str) -> int | None:
    if _any(text, JUST_NOW):
        return 2
    m = TIME_RE.search(text)
    if m:
        n = float(m.group(1))
        unit = m.group(2)
        return int(n if unit.startswith(("min", "मि")) else n * 60)
    m = WORD_TIME_RE.search(text)
    if m:
        n = WORD_NUM[m.group(1)]
        unit = m.group(2)
        return int(n if unit.startswith(("min", "मि")) else n * 60)
    if _any(text, YESTERDAY):  # added after held-out run 1 (h-en-vomit-blood)
        return 720
    return None


BIT_IDIOM = re.compile(r"\b(a|little|tiny|quite a|bit by bit|one)\s+bit\b(?!\s+(him|her|me|my|his|them|us|you|on|by))")


NO_BITE_SEEN = re.compile(r"(?:no|without)\s+(?:bite|bite mark|bite marks|mark|marks|wound|fang marks?)\b|"
                          r"(?:nishaan|nishan|ghav|ghaav|घाव|निशान)\s+(?:\S+\s+)?(?:nahi|nahin|नहीं)|कोई\s+(?:घाव|निशान)")
SUCKED_BLOOD = re.compile(r"(?:khoon|khun|blood|खून)\s+(?:\S+\s+)?(?:choos|chus|suck|चूस)|(?:suck|sucked|choos\w*)\s+(?:out\s+)?(?:the\s+)?(?:blood|khoon|खून)")
AGE = re.compile(r"(\d{1,2})\s*(?:-\s*)?(?:year|years|yr|yrs|saal|sal|varsh|साल|वर्ष)")


THORN = ["thorn", "kaanta", "kanta", "kaante", "needle", "sui", "suii", "glass", "nail", "keel", "splinter",
         "काँटा", "कांटा", "सुई", "कील", "शीशा"]
WEAK_BITE = ["attack", "attacked", "struck", "strike", "hamla"]
WEAK_PAST = ["attacked", "struck", "hamla kiya", "hamla kar", "hamla ho", "ne hamla"]
PERSON = ["my", "me", "i ", "him", "her", "his", "son", "daughter", "father", "mother", "wife", "husband", "brother",
          "sister", "child", "baby", "papa", "mummy", "maa", "bhai", "behen", "beta", "beti", "mere", "meri", "mera",
          "ko", "uncle", "aunty", "dada", "dadi", "nana", "nani", "friend", "someone", "somebody", "kisi",
          "मेरे", "मेरी", "मेरा", "को", "पापा", "माँ", "मां", "भाई", "बहन", "बेटा", "बेटी", "बच्चा", "बच्चे", "पति", "पत्नी"]
GENERIC_Q = ["why", "how do", "how to", "what is", "what are", "which snakes", "kyon", "kyun", "kaise", "kya hota",
             "क्यों", "कैसे", "क्या होता"]


def _explicit_animal_biter(text: str, animal_words: list[str]) -> bool:
    """'dog bit me', 'bitten by a dog', 'kutte ne kaata' - the animal is the stated biter."""
    bite_alt = "|".join(re.escape(_norm(w)) for w in BITE if len(w) > 2)
    for w in animal_words:
        a = re.escape(_norm(w))
        if re.search(rf"{a}[a-z\u0900-\u097F]*\s+(?:[^\s,.;!?।]+\s+){{0,2}}?(?:{bite_alt})", text):
            return True
        if re.search(rf"(?:{bite_alt})\S*\s+(?:by\s+)?(?:a\s+|the\s+)?{a}", text):
            return True
    return False


def parse(raw: str) -> Facts:
    text = _norm(raw)
    text = BIT_IDIOM.sub(" ", text)
    no_bite_seen = bool(NO_BITE_SEEN.search(text))
    text = SUCKED_BLOOD.sub(" choos ", text)  # sucking blood is a thing done, not a bleeding sign
    f = Facts(lang=_detect_lang(raw, text))
    f.snake = _any(text, SNAKE)
    f.bite = _any(text, BITE)
    f.unknown_bite = _any(text, UNKNOWN)
    explicit_animal = False
    if not f.snake:
        for animal, words in OTHER.items():
            if _any(text, words):
                f.other_animal = animal
                explicit_animal = _explicit_animal_biter(text, words)
                break
    if not f.unknown_bite and (f.bite or f.other_animal) and _any(text, HEDGE):
        f.unknown_bite = True
    if f.other_animal and explicit_animal:
        f.unknown_bite = False  # "a dog bit my son, maybe rabies?" is a dog bite, not a mystery bite
    if _any(text, THORN) and not f.snake:
        f.unknown_bite = False  # "kaanta chubh gaya" is a thorn
        if not _any(text, [w for w in BITE if w not in ("prick",)]):
            f.bite = False
    person = _any(text, PERSON)
    weak_only = f.bite and _any(text, WEAK_BITE) and not _any(text, [w for w in BITE if w not in WEAK_BITE])
    if weak_only and not person and not _any(text, WEAK_PAST):
        f.bite = False  # "how to protect from snake attack", "why do snakes strike"
    f.generic_question = _any(text, GENERIC_Q) and not person
    f.prevention = _any(text, PREVENT)
    f.self_harm = _any(text, SELF_HARM)
    for flag, words in FLAG_WORDS.items():
        if _any(text, words):
            if _negated(text, words, flag):
                f.negated.append(flag)
            else:
                f.red_flags.append(flag)
    f.swelling = _any(text, SWELLING) and not _negated(text, SWELLING, "swelling")
    for key, words in DONE.items():
        if _any(text, words):
            setattr(f, key, True)
    # "tied" in "tied a cloth loosely" is still a band; we keep it (safer to warn).
    f.child = _any(text, CHILD)
    m = AGE.search(text)
    if m and int(m.group(1)) < 13:
        f.child = True
    f.pregnant = _any(text, PREGNANT)
    f.minutes_since = _minutes(text)
    for state, words in STATES.items():
        if _any(text, words):
            f.state = state
            break
    symptoms = set(f.red_flags) & {"ptosis", "weakness", "vomiting_abdominal", "unconscious", "breathing", "speech_swallow"}
    f.night_floor = _any(text, NIGHT_FLOOR) or "sleeping on the floor" in text
    if not f.snake and (not f.bite or no_bite_seen) and f.night_floor and symptoms:
        f.occult_krait = True
    return f


def known_flag_keys() -> list[str]:
    return list(RED_FLAGS.keys())
