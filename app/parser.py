"""Keyword parser: free text (English, Hindi in Devanagari, Hinglish) -> facts.

Deterministic and offline. The optional LLM parser (llm.py) can only ADD facts on
top of this one, never remove a danger sign this parser found.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
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
    contact: bool = False
    snake_mention_only: bool = False  # "snake plant care tips", "snakes and ladders rules"  # wound, marks, pain, swelling, or a snake touching a body part
    night_floor: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    s = s.replace("ँ", "ं")  # candrabindu -> anusvara: साँप == सांप
    return re.sub(r"\s+", " ", s).strip()


@lru_cache(maxsize=4096)
def _word_re(w: str):
    return re.compile(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])")


@lru_cache(maxsize=4096)
def _norm_cached(w: str) -> str:
    return _norm(w)


@lru_cache(maxsize=4096)
def _deva_re(w: str):
    # word START boundary only, so suffixes still match ("पलक" in "पलकें") but "कल" does not match inside "निकल"
    return re.compile(r"(?<![\u0900-\u097F])" + re.escape(_norm(w)))


def _any(text: str, words) -> bool:
    for w in words:
        if DEVANAGARI.search(w):
            if _deva_re(w).search(text):
                return True
        elif not w.isascii():
            if _norm_cached(w) in text:
                return True
        elif _word_re(w).search(text):
            return True
    return False


SNAKE = ["snaek", "snkae", "snkebite", "snke", "sanke", "snakee", "pambu", "paambu", "haavu", "hav kad", "🐍", "साप", "sap ne", "snake", "snakes", "snakebite", "saanp", "saap", "sanp", "saamp", "samp", "saap ne", "naag", "nag ne",
         "cobra", "krait", "karait", "kraitt", "viper", "snakbite", "snakebit", "snek", "snak", "snakes bite", "russell", "russells", "ghonas", "sarp", "sarpdansh", "serpent",
         "साँप", "सांप", "सर्प", "नाग", "करैत", "कोबरा", "वाइपर", "घोणस", "सर्पदंश", "फन"]
BITE = ["chavla", "chavli", "chavle", "chavala", "dash diya", "dansh diya", "dank mara", "kat lia", "kaat lia", "bitt", "bitn", "biten", "bittn", "bited", "kat gaya", "kaat gaya", "kat liya", "kadichi", "kadichiruchu", "kadise", "kachchi", "चावला", "चावले", "चावली", "हमला", "got papa", "got mummy",
        "got dad", "got mom", "got bhai", "bite", "bit", "bitten", "biting", "bites", "kaata", "kata", "kaat", "kaatа", "kaat liya", "kaat diya", "kat liya",
        "daswa", "dasa", "dans", "dansh", "dank", "sting", "stung", "attack", "attacked", "struck", "strike",
        "hamla", "got my", "got him", "got her", "fang", "fangs", "fang marks", "snakbite", "snakebit",
        "काटा", "काट", "डसा", "डस", "डंस", "दंश", "डंक"]
UNKNOWN = ["kisi cheez ne", "किसी चीज़ ने", "किसी चीज ने", "something nipped", "something grabbed", "something bit", "something has bitten", "kuch ne kaata", "kuch kaat", "kisi ne kaata", "pata nahi kisne",
           "dont know what bit", "don't know what bit", "not sure what bit", "unknown bite", "insect", "keeda", "kida",
           "fang marks", "fang", "fangs", "two marks", "two holes", "two dots", "do nishan", "do nishaan", "chubh",
           "chubha", "chubh gaya", "pricked", "prick", "चुभ", "दो निशान", "long and black", "lamba kala",
           "it was long", "long thin", "thin thing", "lamba patla", "लंबा सा",
           "कुछ ने काटा", "किसी ने काटा", "पता नहीं किसने", "कीड़े", "कीड़ा"]
OTHER = {
    "dog": ["dog", "kutta", "kutte", "kutiya", "कुत्ता", "कुत्ते"],
    "scorpion": ["scorpion", "bichhu", "bichu", "bicchu", "बिच्छू", "बिच्छु"],
    "monkey": ["monkey", "bandar", "बंदर"],
    "bee": ["bee", "bees", "wasp", "honeybee", "madhumakhi", "tatayya", "ततैया", "मधुमक्खी"],
    "rat": ["rat", "mouse", "chuha", "chooha", "चूहा", "चूहे"],
    "lizard": ["lizard", "chipkali", "छिपकली", "girgit"],
    "mosquito": ["mosquito", "mosquitoes", "machhar", "मच्छर"],
    "ant": ["ant", "ants", "cheenti", "chinti", "चींटी"],
    "bedbug": ["bedbug", "bed bug", "khatmal", "खटमल"],
    "other": ["horse", "squirrel", "spider", "centipede", "kankhajura", "kanghajura", "donkey", "pig", "camel", "bat",
              "parrot", "goat", "cow", "buffalo", "ghoda", "गिलहरी", "मकड़ी", "कनखजूरा"],
    "cat": ["cat", "billi", "बिल्ली"],
}
# Doubt words only count together with a bite word or a named animal ("maybe a rat bit me").
HEDGE = ["in the dark", "andhere", "andhere mein", "something", "kuch", "maybe", "shayad", "not sure", "pata nahi",
         "i guess", "i think", "or something", "ya kuch aur", "pakka nahi", "ho sakta", "we think", "i thought",
         "was it", "thought it was", "lagta hai", "shayad", "dunno", "don't know what", "dont know what",
         "assumed", "nobody saw", "didn't see", "did not see", "dikha nahi", "hoga", "could have been",
         "not 100", "पता नहीं", "could be", "might have been", "may be a",
         "may have been", "might be", "i think", "lagta hai", "अंधेरे", "शायद", "पता नहीं", "कुछ"]
PREVENT = ["prevent", "prevention", "avoid", "stay safe", "keep away", "keep snakes out", "keep snakes away",
           "repel", "repellent", "door gap", "keep it away", "keep it out", "keep them out", "keep them away",
           "door kaise rakhe", "door rakhe", "bhagane", "bhagaye", "protect", "bachav", "bachaav", "kaise bache",
           "kaise bachein", "how to be safe", "बचाव", "बचें", "बचे", "रोकथाम"]
SELF_HARM = ["suicide", "kill myself", "end my life", "self harm", "self-harm", "want to die", "aatmahatya",
             "marna chahta", "marna chahti", "jeena nahi", "jina nahi", "khud ko khatam", "zindagi khatam",
             "आत्महत्या", "मरना चाहता", "मरना चाहती"]

FLAG_WORDS = {
    "ptosis": ["droop", "drooping", "droopy", "eyelid", "eyelids", "ptosis", "double vision", "blurred vision",
               "sees double", "seeing double", "see double", "everything double", "vision is blurred",
               "eyes not opening", "eyes are not opening", "eyes won't open", "half closed", "half-closed",
               "eyes keep shutting", "keep shutting", "eyes keep closing", "looks drunk", "cannot see properly", "can't see properly", "cant see properly", "seeing double", "aankh nahi khul", "aankhen nahi khul", "aankhein nahi khul",
               "palke gir", "palken gir", "palke jhuk", "palken jhuk", "aankhen jhuk", "jhuk rahi", "palke bhaari",
               "palken bhaari", "पलकें गिर", "आँखें नहीं खुल", "आंखें नहीं खुल",
               "blurry", "can't open eyes", "cannot open eyes", "cant open eyes", "eyes closing", "eyes are closing",
               "aankh band", "aankhen band", "aankhein band", "ankh band", "open his eyes", "open her eyes",
               "open their eyes", "open my eyes", "eyes heavy", "keep eyes open", "keep his eyes open", "palak", "palken", "dhundhla", "do do dikh",
               "पलक", "पलकें", "आंख बंद", "आंखें बंद", "धुंधला", "दो दो दिख", "आंखें नहीं खुल", "आंख नहीं खुल"],
    "breathing": ["breath", "breathe", "breathing", "breathless", "short of breath", "choking", "saans", "sans",
                  "gasping", "gasp", "haanf", "hanf", "haanp", "blue lips", "lips blue", "lips turning blue",
                  "lips are turning blue", "lips are blue", "turning blue", "breaths are", "far apart", "neela pad",
                  "struggling to get air", "get air", "gone blue", "blue around the mouth", "can't get air",
                  "chest tight", "chest tightness", "chhati jakad", "हांफ", "होंठ नीले",
                  "saas", "dam ghut", "dum ghut", "सांस", "दम घुट", "श्वास"],
    "speech_swallow": ["slurred", "can't speak", "cannot speak", "cant speak", "can't swallow", "cannot swallow",
                       "difficulty swallowing", "trouble swallowing", "unable to swallow",
                       "slurring", "gala band", "gale me kuch", "गला बंद", "spitting", "saliva", "tongue feels thick",
                       "thick tongue", "words are coming out wrong", "ladkhada", "aawaz ladkha", "awaaz ladkha",
                       "voice has gone", "voice gone", "talking like he is drunk", "talking like she is drunk",
                       "like he is drunk", "like she is drunk", "frothing", "froth", "jhaag", "झाग", "trouble speaking", "bol nahi", "bol nhi",
                       "nigal nahi", "nigalne", "awaaz", "आवाज़", "बोल नहीं", "निगल", "बोलने में"],
    "bleeding": ["bleeding", "bleed", "blood", "khoon", "khun", "gums", "nosebleed", "nose bleed", "red urine",
                 "urine is red", "urine red", "peshab laal", "laal peshab", "pishab laal", "blood in urine",
                 "like cola", "cola", "coca", "black urine", "pee is", "पेशाब काला", "peshab kala", "kala peshab",
                 "dark urine", "black urine", "brown urine", "naak se", "masood", "खून", "मसूड़", "नाक से", "लाल पेशाब",
                 "काला पेशाब", "रक्त"],
    "unconscious": ["unconscious", "fainted", "fainting", "faint", "drowsy", "not responding", "unresponsive",
                    "collapsed", "collapse", "passed out", "pass out", "fits", "fit aa", "seizure", "seizures",
                    "having a fit", "a fit", "shaking all over", "jag nahi raha", "jag nahi rahi", "jaag nahi",
                    "uth nahi raha", "uth nahi rahi", "जाग नहीं", "उठ नहीं",
                    "convulsion", "convulsions", "jhatke", "jhatka", "hosh me nahi", "hosh mein nahi", "sleepy",
                    "neend aa rahi", "बहुत नींद", "झटके", "दौरा",
                    "not waking", "won't wake", "hard to wake", "behosh", "behoshi", "hosh nahi", "sust",
                    "बेहोश", "होश नहीं", "सुस्त", "बेसुध"],
    "weakness": ["weak", "weakness", "paralysis", "paralysed", "paralyzed", "can't move", "cannot move",
                 "can't hold his head", "can't hold her head", "cannot hold head", "can't hold head", "head drop",
                 "head falling", "gardan latak", "gardan gir", "no strength", "no power", "jaan nahi", "गर्दन लटक",
                 "floppy", "can't lift", "cannot lift", "cant lift", "lift his head", "lift her head", "dheela",
                 "शरीर ढीला", "ढीला", "dheele", "dheela pad", "gardan sambhal nahi", "गर्दन नहीं संभल", "sambhal nahi",
                 "head keeps falling", "head falling forward",
                 "can't stand", "cannot stand", "limp", "kamzori", "kamjori", "lakwa", "lakva", "kamzor",
                 "कमज़ोरी", "कमजोरी", "कमज़ोर", "कमजोर", "लकवा", "हिल नहीं"],
    "vomiting_abdominal": ["vomit", "vomiting", "vomited", "throwing up", "stomach pain", "abdominal pain",
                           "belly pain", "stomach ache", "ulti", "ultee", "pet dard", "pet me dard", "pet mein dard",
                           "उल्टी", "पेट दर्द", "पेट में दर्द"],
}
SWELLING = ["swelling", "swollen", "swell", "sujan", "soojan", "sooj", "suj", "suj gaya", "suj raha", "suj rahi",
            "puffy", "fool gaya", "phool gaya", "सूजन", "सूज", "फूल गया"]
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
NEG_BEFORE = re.compile(r"(?:\bno\b|\bwithout\b|\bdenies\b)\s+(?:(?:difficulty|trouble|problem|problems|"
                        r"sign|signs|issue|issues|sign of|signs of|active|visible)\s+)?$")
NORMAL_AFTER = re.compile(r"^\s*(?:is\s+|are\s+|hai\s+|है\s+)?(?:normal|normally|fine|ok|okay|theek|thik|ठीक|सामान्य)"
                          r"(?![^,.;!?।]{0,12}(?:\bnot\b|\bnahi\b|\bnahin\b|\bnhi\b|\bna\b|नहीं|नही))")
HI_NEG_AFTER = re.compile(r"^\s*(?:aa\s+|aa raha\s+|आ\s+)?(?:nahi|nahin|nhi|नहीं|नही)\b"
                          r"(?!\s*(?:ruk|ruka|rukta|rukti|rok|tham|tham\w*|thahar|thehar|jam|jamta|jam raha|band|"
                          r"रुक|रोक|थम|ठहर|जम|बंद))")
WORSENING = re.compile(r"\b(?:but|lekin|magar|par|worse|worsening|getting|badh|badhti|badh raha)\b|लेकिन|मगर|बढ़|बिगड़")
NEG_QUALIFIED = re.compile(r"(?:difficulty|trouble|problem|problems|sign|signs|issue|issues|sign of|signs of|"
                           r"active|visible)\s+$")
QUALIFIER_AFTER = re.compile(r"^\s*(?:problem|problems|trouble|issue|issues|difficulty|ki dikkat|ki problem|"
                             r"me dikkat|mein dikkat|takleef)\b")
QUESTION_CLAUSE = re.compile(r"(?:\bis\b|\bhow\b|\bkya\b|क्या|\bif\b)[^,.;!?।]*$")
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
            neg_before = bool(NEG_BEFORE.search(before))
            if (neg_before and flag not in PRESENCE_TYPE and not NEG_QUALIFIED.search(before)
                    and not QUALIFIER_AFTER.match(after)):
                neg_before = False  # bare "no breathing" = not breathing (respiratory arrest), STG p.20
            normal_after = bool(NORMAL_AFTER.search(after))
            clause = text[max(0, m.start() - 30): m.end() + 30]
            if normal_after and ("?" in text[m.end(): m.end() + 30] or QUESTION_CLAUSE.search(before[-25:])):
                normal_after = False  # "is his breathing ok?" is a question, not a denial
            denied = neg_before or normal_after
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


THORN = ["thorn", "kaanta", "kanta", "kaante", "needle", "sui", "suii", "keel", "splinter",
         "sewing", "silai", "stitching",
         "काँटा", "कांटा", "सुई", "कील", "शीशा"]
WEAK_BITE = ["attack", "attacked", "struck", "strike", "hamla", "हमला"]
WEAK_PAST = ["attacked", "struck", "hamla kiya", "hamla kar", "hamla ho", "ne hamla"]
PERSON = ["my", "me", "i ", "him", "her", "his", "son", "daughter", "father", "mother", "wife", "husband", "brother",
          "sister", "child", "baby", "papa", "mummy", "maa", "bhai", "behen", "beta", "beti", "mere", "meri", "mera",
          "ko", "uncle", "aunty", "dada", "dadi", "nana", "nani", "friend", "someone", "somebody", "kisi",
          "मेरे", "मेरी", "मेरा", "को", "पापा", "माँ", "मां", "भाई", "बहन", "बेटा", "बेटी", "बच्चा", "बच्चे", "पति", "पत्नी"]
GENERIC_Q = ["why", "how do", "how to", "what is", "what are", "which snakes", "kyon", "kyun", "kaise", "kya hota",
             "क्यों", "कैसे", "क्या होता"]


ANIMAL_NOT_RE = re.compile(r"mosquito nets?|machhardani|मच्छरदानी|rat holes?|rat ka bil|chuhe ka bil|\brat\s+(?:ko|me|mein|bhar|ke)\b")
VICTIM_RE = re.compile(r"\b(?:was|got|been|get|gets|getting|is)\s+(?:just\s+)?(?:bit|bitten|stung)\b|\bjust bit\b")
GENERAL_GROUP = ["my family", "my home", "my house", "my village", "my kids from", "my children from", "my farm",
                 "my field", "my garden", "parivar", "ghar ko", "घर को", "परिवार"]
NOUN_BITE = ["snakebite", "snake bite", "snake bites", "snakebites", "sarpdansh", "सर्पदंश", "bite", "bites", "kaatte",
             "kaatta", "kaat"]
INFO_WORDS = ["tips", "game", "plant", "pose", "species", "project", "show", "tickets", "race", "boat", "rules", "film",
              "movie", "song", "documentary", "photo", "picture", "facts", "information", "learn", "study", "school",
              "kaise", "kya", "kaun", "jaankari", "what", "how", "which", "where", "when", "repellent", "keep"]
GENERIC_ANY = ["kyon", "kyun", "why do", "why does", "how many", "kitne log", "kitne logon", "क्यों", "कितने"]
MARK_WORDS = ["mark", "marks", "nishan", "nishaan", "निशान", "puncture", "punctures", "holes", "dots", "daag", "lal daag",
              "spots", "red spots", "fang"]
PRICK_WORDS = ["stepped on", "touched", "touch", "pinch", "pinched", "nipped", "injection", "sting like", "kisi cheez", "किसी चीज़", "किसी चीज",
               "prick", "pricked", "chubh", "chubha", "chubhan", "chubi", "grabbed", "something", "kuch laga",
               "कुछ लगा", "stung", "sting", "nipped", "nip"]
GOT_PERSON = ["got papa", "got mummy", "got dad", "got mom", "got bhai", "got my", "got him", "got her", "got me"]
WOUND_WORDS = ["wound", "wounds", "ghav", "ghaav", "घाव", "touched", "touch", "chhua", "chhu gaya", "छुआ"]
HUMAN_BITER = re.compile(r"\b(?:baby|toddler|child|kid|son|daughter|brother|sister|bachcha|bachche|year old)\s+"
                         r"(?:bit|bites|biting)\s+(?:my|me|him|her|his|other|the|a)\b"
                         r"|\bbit my (?:tongue|lip|lips|cheek|nails?)\b|teeth marks from (?:my|a|the) "
                         r"(?:baby|toddler|child|kid|son|daughter)|\b(?:toddler|baby) biting|\bwhen i bite\b|\bi bite\b"
                         r"|(?:बच्चे|बच्चा|बच्ची|बेबी)\s+ने\s+(?:मेरी|मेरा|मेरे|उसकी|उसका|उसके|अपनी|अपना)\s+\S+\s+काट")
INJURY = ["fell", "fall", "fallen", "stairs", "gir gaya", "gir gayi", "slipped", "accident", "गिर"]
MARKS_RE = re.compile(r"\b(?:two|2|do|दो)\s+(?:(?:small|tiny|red|little|chhote|lal|bleeding|deep|clean)\s+){0,2}"
                      r"(?:marks?|holes?|dots?|spots?|points?|punctures?|puncture wounds?|wounds|nishan|nishaan|daag|daant|"
                      r"daant ke nishaan|निशान|छेद|घाव)")
HEDGE_IGNORE_RE = re.compile(r"(?:maybe|shayad|i think|i guess)\s+(?:\S+\s+){0,3}?(?:rabies|rabid|pagal|vaccine|injection|"
                             r"infection|infected|allergic|allergy|serious|khatra)\S*|i think it needs|kuch upay|upay batao|"
                             r"maybe (?:rabies|infection|infected|allergic|allergy|serious)|kuch karo|kuch karein|"
                             r"what to do|kya karu|kya karun|kya karein|kya kare|not sure what to do|"
                             r"not sure if (?:it'?s |this is )?serious|कुछ करो|क्या करें")
LIKE_RE = re.compile(r"\b(?:like|jaisa|jaise|jaisi)\b|-like|जैसा|जैसे")
OUTDOOR = ["handpump", "hand pump", "canal", "garden", "bhoosa", "bhoose", "dung", "shed", "sugarcane", "rice field", "tea", "woodpile", "haystack", "cattle shed", "cowshed", "water channel", "well",
           "dhaan", "field", "fields", "paddy", "grass", "farm", "khet", "jungle", "forest", "garden", "bushes", "dark",
           "andhere", "खेत", "घास", "जंगल", "अंधेरे"]
BODY_CHANGE = ["screaming", "scream", "rote hue", "rota hua", "roti hui", "rote", "रोता", "रोती", "रो रहा", "रो रही",
               "bhaari", "heavy", "burns", "pain", "painful", "dard", "jalan", "burning", "crying", "ro raha", "ro rahi", "rona", "red dots",
               "bleeding", "khoon", "hurts", "hurting", "throbs", "throbbing", "tingling", "tingle", "numb", "sunn",
               "jhanjhanahat", "tees", "झनझनाहट", "सुन्न", "dizzy", "chakkar", "चक्कर", "blue", "neela", "नीला",
               "दर्द", "जलन"]
SOMETHING_TOUCHED = ["stepped on something", "something slid", "slid over", "something touched", "something pricked",
                     "something stung", "kuch chubha", "kuch laga", "kuch chhua", "पैर पड़ा", "कुछ चुभा"]
URGENCY = ["hlp", "halp", "help", "fast", "quick", "quickly", "just now", "abhi", "jaldi", "bachao", "turant", "emergency",
           "bachav karo", "bachaav karo", "बचाव करो", "बचाओ", "pls",
           "मदद", "जल्दी", "बचाओ", "अभी"]
BODY_PARTS = ["toe nail", "nail", "ungli", "leg", "foot", "feet", "hand", "arm", "ankle", "finger", "toe", "pair", "haath", "ungli", "पैर", "हाथ",
              "heel", "knee", "thigh", "shin", "calf", "wrist", "palm", "sole", "angutha", "एड़ी", "उंगली", "anguli"]
SPECIFIC_PERSON = ["son", "daughter", "father", "mother", "wife", "husband", "brother", "sister", "child", "baby",
                   "papa", "mummy", "maa", "bhai", "behen", "beta", "beti", "uncle", "aunty", "dada", "dadi", "nana",
                   "nani", "grandma", "grandpa", "grandmother", "grandfather", "kid", "dad", "mom", "बेटा", "बेटी",
                   "बेटे", "पापा", "माँ", "भाई", "बहन", "बच्चा", "बच्चे"]
SELF_BITE = re.compile(r"\bwhen i bite\b|\bbite my food\b|\bbit my (?:own )?(?:tongue|lip|lips|cheek)\b|\bbit into\b"
                       r"|काटता है|kaatta hai|katta hai|bites everything|सब कुछ काटता|teething|दांत निकल")
GENERIC_START = re.compile(r"^\s*(?:how to|how do|how can|why|what is|what are|what should|which|is there|are there|"
                           r"where is|where can|can i|do you|kaise|kyon|kyun|kya hota|kya koi|"
                           r"क्यों|कैसे)\b")
DROOL = ["drool", "drooling", "lar tapak", "laar", "लार"]


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
    # SAFETY RULE for this block: doubt always resolves toward the hospital. A signal may only be
    # removed by can_suppress(): no danger sign, no swelling/pain/marks, not outdoors or at night,
    # no doubt words, no "was/got bit" victim phrasing. Everything else errs toward care.
    f.unknown_bite = _any(text, UNKNOWN) or bool(MARKS_RE.search(text))
    if not f.snake:
        for animal, words in OTHER.items():
            if _any(text, words):
                f.other_animal = animal
                break
    t_animal = ANIMAL_NOT_RE.sub(" ", text)
    if f.other_animal and not any(_any(t_animal, w) for w in OTHER.values()):
        f.other_animal = None  # "mosquito net", "rat hole", "rat ko" (= raat, night)
    t_doubt = HEDGE_IGNORE_RE.sub(" ", text)  # "maybe rabies?", "kuch karo" are not doubts about the biter
    doubt = _any(t_doubt, HEDGE)
    if not f.unknown_bite and (f.bite or f.other_animal) and doubt:
        f.unknown_bite = True
    night = _any(text, NIGHT_FLOOR) or _any(text, ["at night", "raat", "night", "रात"])
    outdoor = _any(text, OUTDOOR) or night
    flag_hit = any(_any(text, w) for w in FLAG_WORDS.values())
    swelling = _any(text, SWELLING)
    body_change = swelling or _any(text, BODY_CHANGE) or _any(text, MARK_WORDS) or flag_hit
    victim = bool(VICTIM_RE.search(text))
    if victim:
        f.bite = True
    urgent = _any(text, URGENCY) or "!" in raw

    def can_suppress(allow_marks: bool = False, allow_outdoor: bool = False) -> bool:
        marks = bool(MARKS_RE.search(text)) or _any(text, MARK_WORDS)
        return not (flag_hit or swelling or _any(text, BODY_CHANGE) or (marks and not allow_marks)
                    or (outdoor and not allow_outdoor) or night or doubt or victim or urgent)

    if SELF_BITE.search(text) and not f.snake and not flag_hit and not swelling and not victim:
        f.bite = False  # "my tooth hurts when i bite", "I bit my tongue while eating"
        if not (MARKS_RE.search(text) or _any(text, MARK_WORDS)):
            f.unknown_bite = False

    # Narrow suppressions (each only when nothing in the message points to harm)
    if f.bite and not f.snake and HUMAN_BITER.search(text) and can_suppress(allow_marks=True):
        f.bite = False  # "my baby bit my finger", "I bit my tongue", "my 2 year old bites other kids"
        f.unknown_bite = False
    if MARKS_RE.search(text) and not f.snake and _any(text, INJURY) and can_suppress(allow_marks=True):
        f.unknown_bite = False  # "fell and has two marks on his knee from the stairs"
    explicit_bite_word = _any(text, ["bit", "bitten", "bite", "kaata", "kata", "kaat", "काटा", "काट", "dasa", "डसा",
                                     "kat gaya", "kaat gaya", "kadichi"])
    thorn_suppressed = False
    if (_any(text, THORN) and not f.snake and not LIKE_RE.search(text) and not explicit_bite_word
            and can_suppress()):
        thorn_suppressed = True
        f.unknown_bite = False  # "kaanta chubh gaya pair me", "pricked my finger while sewing"
        f.bite = False
    person = _any(text, PERSON) and not _any(text, GENERAL_GROUP)
    weak_only = f.bite and not _any(text, [w for w in BITE if w not in WEAK_BITE + NOUN_BITE])
    general_q = bool(GENERIC_START.match(text)) or _any(text, GENERIC_ANY)
    if weak_only and general_q and not person and can_suppress(allow_outdoor=True) \
            and not _any(text, WEAK_PAST) and not _any(text, BODY_PARTS):
        f.bite = False  # "why do snakes strike", "how to protect my family from snake attack"
    f.generic_question = general_q and not person and can_suppress(allow_outdoor=True) and not _any(text, BODY_PARTS)

    # Safety net: an injury cue plus any symptom is a possible snakebite unless another animal is
    # clearly the biter (no doubt words).
    injury_cue = (_any(text, BODY_PARTS) or _any(text, MARK_WORDS) or bool(MARKS_RE.search(text)) or f.bite
                  or _any(text, THORN) or _any(text, PRICK_WORDS) or victim)
    explicit_other = f.other_animal and not doubt
    symptom = flag_hit or swelling or _any(text, BODY_CHANGE)  # marks are an injury cue, not a symptom
    human_bite = bool(HUMAN_BITER.search(text)) and not doubt
    real_cue = (f.bite or victim or doubt or _any(text, MARK_WORDS) or bool(MARKS_RE.search(text)) or _any(text, PRICK_WORDS)
                or _any(text, THORN) or (outdoor and _any(text, BODY_PARTS)))
    if not f.snake and not explicit_other and not human_bite and not f.unknown_bite and not thorn_suppressed \
            and not SELF_BITE.search(text):
        if real_cue and symptom:
            f.unknown_bite = True  # "my son got bit on the ankle, now he is vomiting"
        elif outdoor and (_any(text, PRICK_WORDS) or _any(text, THORN)) and _any(text, BODY_PARTS):
            f.unknown_bite = True  # "sui jaisi chubhan hui pair me raat ko"
        elif _any(text, PRICK_WORDS) and _any(text, BODY_PARTS):
            f.unknown_bite = True  # "something nipped her wrist", "felt a pinch on my toe"
        elif doubt and (_any(text, MARK_WORDS) or bool(MARKS_RE.search(text))):
            f.unknown_bite = True  # "pata nahi kya tha ... pair par nishaan"
    if human_bite and symptom and not f.snake and not SELF_BITE.search(text):
        f.unknown_bite = True  # "my toddler bit my son?? ... his foot is swelling" - check it
    words = re.findall(r"\w+", text)
    info_marker = ("?" in raw or bool(GENERIC_START.match(text)) or _any(text, GENERIC_ANY)
                   or _any(text, INFO_WORDS))
    f.snake_mention_only = (f.snake and info_marker and not f.bite and not f.unknown_bite and not urgent and not doubt
                            and not flag_hit and not swelling and not _any(text, BODY_CHANGE) and not victim
                            and not _any(text, BODY_PARTS) and not _any(text, GOT_PERSON) and len(words) >= 3
                            and not _any(text, SPECIFIC_PERSON) and not night)
    f.contact = (bool(MARKS_RE.search(text)) or _any(text, WOUND_WORDS) or body_change
                 or (f.snake and (_any(text, BODY_PARTS) or victim or _any(text, GOT_PERSON)
                                  or _any(text, SPECIFIC_PERSON))))
    if f.snake or f.bite:
        if _any(text, DROOL):
            f._drool = True
    f.prevention = _any(text, PREVENT)
    f.self_harm = _any(text, SELF_HARM)
    for flag, words in FLAG_WORDS.items():
        if _any(text, words):
            if _negated(text, words, flag):
                f.negated.append(flag)
            else:
                f.red_flags.append(flag)
    if getattr(f, "_drool", False) and "speech_swallow" not in f.red_flags:
        f.red_flags.append("speech_swallow")  # drooling after a bite = can't swallow (neurotoxic)
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
