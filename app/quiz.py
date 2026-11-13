"""The 3-minute check: six life-or-death decisions, asked before and after a short lesson.

Each concept has two parallel scenarios (form A and form B). Every session gets a
random assignment of which form is the 'before' test and which is the 'after'
test (counterbalancing), so a difference between forms cannot pose as learning.
"""
from __future__ import annotations

import random

CONCEPTS = {
    "tourniquet": {"en": "No tight bands", "hi": "कसकर न बाँधें", "lesson": "dont_tourniquet"},
    "healer": {"en": "Hospital, not healer", "hi": "ओझा नहीं, अस्पताल", "lesson": "dont_healer"},
    "cut_suck": {"en": "Never cut or suck", "hi": "न काटें, न चूसें", "lesson": "dont_cut_suck"},
    "no_wait": {"en": "Go even without symptoms", "hi": "लक्षण न हों तब भी जाएँ", "lesson": "go_hospital"},
    "krait": {"en": "Painless night bites (krait)", "hi": "रात का बिना दर्द का दंश (करैत)", "lesson": "suspect_krait"},
    "still": {"en": "Keep still, remove rings", "hi": "स्थिर रखें, गहने उतारें", "lesson": "immobilise"},
}

# options: (id, en, hi, correct, dangerous)
Q = {
    ("tourniquet", "A"): {
        "en": "A snake bites Ramesh on the ankle in the field. A neighbour says: tie a rope tightly above the bite to stop the poison. What do you do?",
        "hi": "खेत में रमेश के टखने पर साँप काटता है। पड़ोसी कहता है: ज़हर रोकने के लिए दंश के ऊपर रस्सी कसकर बाँध दो। आप क्या करेंगे?",
        "options": [
            ("a", "Tie the rope tightly above the bite", "दंश के ऊपर रस्सी कसकर बाँध देंगे", False, True),
            ("b", "Tie it, and loosen it every 10 minutes", "बाँधेंगे, और हर 10 मिनट में ढीली करेंगे", False, True),
            ("c", "Tie nothing. Keep the leg still and go to hospital", "कुछ नहीं बाँधेंगे। पैर स्थिर रखकर अस्पताल जाएँगे", True, False),
            ("d", "Tie it and wait to see if swelling comes", "बाँधकर देखेंगे कि सूजन आती है या नहीं", False, True),
        ],
    },
    ("tourniquet", "B"): {
        "en": "Sunita is bitten on the hand while cutting grass. Her brother wants to tie a string tightly around her arm. Your advice?",
        "hi": "घास काटते समय सुनीता के हाथ पर साँप काटता है। उसका भाई बाँह पर धागा कसकर बाँधना चाहता है। आपकी सलाह?",
        "options": [
            ("a", "Good idea, tie it close to the bite", "अच्छा है, दंश के पास बाँध दो", False, True),
            ("b", "Only tie it if it was a cobra", "सिर्फ़ कोबरा हो तो बाँधो", False, True),
            ("c", "Tie it until you reach a healer", "ओझा तक पहुँचने तक बाँधे रखो", False, True),
            ("d", "Don't. Tight bands can kill the arm. Keep it still, go to hospital", "मत बाँधो। कसा बंधन हाथ को सड़ा सकता है। हाथ स्थिर रखो, अस्पताल चलो", True, False),
        ],
    },
    ("healer", "A"): {
        "en": "The village ojha (healer) is 5 minutes away. The government hospital is 40 minutes away. Where do you take the person first?",
        "hi": "गाँव का ओझा 5 मिनट दूर है। सरकारी अस्पताल 40 मिनट दूर है। आप पहले कहाँ ले जाएँगे?",
        "options": [
            ("a", "The ojha first, he is closer", "पहले ओझा के पास, वह नज़दीक है", False, True),
            ("b", "Straight to the hospital: only antivenom works", "सीधे अस्पताल: सिर्फ़ एंटीवेनम असर करता है", True, False),
            ("c", "Wait at home to see if it was poisonous", "घर पर रुककर देखेंगे कि ज़हरीला था या नहीं", False, True),
            ("d", "The ojha, then hospital if it gets worse", "ओझा, फिर हालत बिगड़े तो अस्पताल", False, True),
        ],
    },
    ("healer", "B"): {
        "en": "Before leaving for the hospital, relatives want to put a black stone and a herbal paste on the bite. You:",
        "hi": "अस्पताल निकलने से पहले रिश्तेदार दंश पर काला पत्थर और जड़ी-बूटी का लेप लगाना चाहते हैं। आप:",
        "options": [
            ("a", "Let them, the stone pulls the venom out", "लगाने देंगे, पत्थर ज़हर खींच लेता है", False, True),
            ("b", "Apply the paste and wait one hour", "लेप लगाकर एक घंटा रुकेंगे", False, True),
            ("c", "Skip it and leave for the hospital now", "यह छोड़कर अभी अस्पताल निकलेंगे", True, False),
            ("d", "Do a mantra first, then decide", "पहले मंत्र, फिर तय करेंगे", False, True),
        ],
    },
    ("cut_suck", "A"): {
        "en": "Should you cut the bite with a blade and suck the venom out?",
        "hi": "क्या दंश को ब्लेड से काटकर ज़हर चूसना चाहिए?",
        "options": [
            ("a", "Yes, quickly, before it spreads", "हाँ, जल्दी, फैलने से पहले", False, True),
            ("b", "Only if the bite is bleeding", "सिर्फ़ अगर दंश से खून आ रहा हो", False, True),
            ("c", "No: it doesn't remove venom and causes bleeding and infection", "नहीं: इससे ज़हर नहीं निकलता, खून बहता है और संक्रमण होता है", True, False),
            ("d", "Cut it but don't suck", "काटें पर चूसें नहीं", False, True),
        ],
    },
    ("cut_suck", "B"): {
        "en": "In a film, the hero sucks the venom out of a snakebite. In real life you should:",
        "hi": "फ़िल्म में हीरो सर्पदंश से ज़हर चूस लेता है। असल ज़िंदगी में आपको:",
        "options": [
            ("a", "Do the same, it works", "वही करना चाहिए, यह काम करता है", False, True),
            ("b", "Never cut or suck; keep the limb still and go to hospital", "कभी न काटें, न चूसें; अंग स्थिर रखकर अस्पताल जाएँ", True, False),
            ("c", "Burn the bite with a hot iron instead", "इसकी जगह गरम लोहे से दंश जलाएँ", False, True),
            ("d", "Rub salt into the bite", "दंश पर नमक रगड़ें", False, True),
        ],
    },
    ("no_wait", "A"): {
        "en": "Someone was bitten 20 minutes ago. There is no pain and no swelling. What now?",
        "hi": "किसी को 20 मिनट पहले साँप ने काटा। न दर्द है, न सूजन। अब क्या?",
        "options": [
            ("a", "Relax, it was not poisonous", "आराम करें, ज़हरीला नहीं था", False, True),
            ("b", "Go to hospital now: some venom acts hours later", "अभी अस्पताल जाएँ: कुछ ज़हर घंटों बाद असर करते हैं", True, False),
            ("c", "Wait till morning and see", "सुबह तक रुककर देखें", False, True),
            ("d", "Put turmeric on it and rest", "हल्दी लगाकर आराम करें", False, True),
        ],
    },
    ("no_wait", "B"): {
        "en": "The snake was small and the bite is just two tiny dots. Should the person still go to hospital?",
        "hi": "साँप छोटा था और दंश बस दो छोटे निशान हैं। क्या फिर भी अस्पताल जाना चाहिए?",
        "options": [
            ("a", "No, small snakes are harmless", "नहीं, छोटे साँप हानिरहित होते हैं", False, True),
            ("b", "Only if it starts hurting", "सिर्फ़ अगर दर्द शुरू हो", False, True),
            ("c", "Yes, now: you cannot tell venom from the size or the marks", "हाँ, अभी: आकार या निशान से ज़हर का पता नहीं चलता", True, False),
            ("d", "Call the healer to check", "जाँच के लिए ओझा को बुलाएँ", False, True),
        ],
    },
    ("krait", "A"): {
        "en": "A child who slept on the floor wakes at 4 a.m. with stomach pain and drooping eyelids. No bite mark is seen. What could it be?",
        "hi": "ज़मीन पर सोया एक बच्चा सुबह 4 बजे पेट दर्द और झुकी पलकों के साथ उठता है। कोई दंश का निशान नहीं दिखता। यह क्या हो सकता है?",
        "options": [
            ("a", "Food poisoning: give ORS and wait", "फ़ूड पॉइज़निंग: ORS देकर इंतज़ार करें", False, True),
            ("b", "Possibly a krait bite: hospital immediately", "शायद करैत का दंश: तुरंत अस्पताल", True, False),
            ("c", "Evil eye: call the healer", "नज़र लगी है: ओझा को बुलाएँ", False, True),
            ("d", "Just tired: let him sleep", "बस थका है: सोने दें", False, True),
        ],
    },
    ("krait", "B"): {
        "en": "Your father slept on the floor. In the morning he is weak, vomiting and can't keep his eyes open. No wound is visible. You:",
        "hi": "आपके पिता ज़मीन पर सोए थे। सुबह वे कमज़ोर हैं, उल्टी कर रहे हैं और आँखें खुली नहीं रख पा रहे। कोई घाव नहीं दिखता। आप:",
        "options": [
            ("a", "Give him tea and let him rest", "चाय देकर आराम करने दें", False, True),
            ("b", "Wait for the local doctor's clinic to open", "स्थानीय डॉक्टर का क्लिनिक खुलने का इंतज़ार करें", False, True),
            ("c", "Treat it as a possible krait bite: call 108, hospital now", "संभावित करैत दंश मानें: 108 पर फ़ोन, अभी अस्पताल", True, False),
            ("d", "Give him a painkiller for the weakness", "कमज़ोरी के लिए दर्द की दवा दें", False, True),
        ],
    },
    ("still", "A"): {
        "en": "On the way to the hospital, what helps the most?",
        "hi": "अस्पताल के रास्ते में सबसे ज़्यादा क्या मदद करता है?",
        "options": [
            ("a", "Let him walk to keep the blood moving", "खून चलता रहे इसलिए चलने दें", False, True),
            ("b", "Keep the limb still, take off rings and bangles, carry him", "अंग स्थिर रखें, अंगूठी-चूड़ियाँ उतारें, उठाकर ले जाएँ", True, False),
            ("c", "Massage the limb to spread the pain", "दर्द कम करने के लिए मालिश करें", False, True),
            ("d", "Give him alcohol for the pain", "दर्द के लिए शराब दें", False, True),
        ],
    },
    ("still", "B"): {
        "en": "A woman is bitten on the hand. She is wearing bangles and a ring. Before you travel:",
        "hi": "एक महिला के हाथ पर दंश है। उसने चूड़ियाँ और अंगूठी पहनी है। निकलने से पहले:",
        "options": [
            ("a", "Leave them on, there's no time", "रहने दें, समय नहीं है", False, True),
            ("b", "Take them off now, before the hand swells", "हाथ सूजने से पहले अभी उतार दें", True, False),
            ("c", "Tie the bangles tighter to stop the venom", "ज़हर रोकने के लिए चूड़ियाँ और कस दें", False, True),
            ("d", "Rub the hand to bring the venom out", "ज़हर निकालने के लिए हाथ रगड़ें", False, True),
        ],
    },
}

ORDER = list(CONCEPTS.keys())


def assign_forms(rng: random.Random | None = None) -> tuple[str, str]:
    rng = rng or random.Random()
    return ("A", "B") if rng.random() < 0.5 else ("B", "A")


def questions(form: str, lang: str, rng: random.Random | None = None) -> list[dict]:
    rng = rng or random.Random()
    out = []
    for c in ORDER:
        q = Q[(c, form)]
        opts = [{"id": o[0], "text": o[2] if lang == "hi" else o[1]} for o in q["options"]]
        rng.shuffle(opts)
        out.append({"concept": c, "form": form, "text": q[lang] if lang in q else q["en"], "options": opts,
                    "concept_label": CONCEPTS[c][lang if lang in ("en", "hi") else "en"]})
    return out


def score(form: str, answers: dict[str, str]) -> dict:
    """answers: {concept: option_id}. Returns per-concept correctness and dangerous choices."""
    per = {}
    for c in ORDER:
        chosen = answers.get(c)
        opts = {o[0]: o for o in Q[(c, form)]["options"]}
        if chosen not in opts:
            per[c] = {"answered": False, "correct": False, "dangerous": False}
            continue
        o = opts[chosen]
        per[c] = {"answered": True, "correct": bool(o[3]), "dangerous": bool(o[4])}
    return {
        "per_concept": per,
        "correct": sum(1 for v in per.values() if v["correct"]),
        "dangerous": sum(1 for v in per.values() if v["dangerous"]),
        "answered": sum(1 for v in per.values() if v["answered"]),
        "total": len(ORDER),
    }


def correct_option(concept: str, form: str) -> str:
    return next(o[0] for o in Q[(concept, form)]["options"] if o[3])
