"""Bilingual guidance content. Every line carries a source key (see SOURCES).

Nothing in here is generated at run time: the protocol engine (protocol.py) only
selects and orders these items. The optional language model never writes advice.
"""

SOURCES = {
    "STG2017": {
        "title": "Standard Treatment Guidelines: Management of Snake Bite, MoHFW / NHM, Government of India (Aug 2017)",
        "url": "https://ncdc.mohfw.gov.in/uploads/pdf/Standard-Treatment-Guidelines-for-Management-of-Snake-Bite.pdf",
    },
    "NP2007": {
        "title": "Indian National Snakebite Protocol, first aid 'Do it R.I.G.H.T.' (Simpson, Indian Pediatrics 44:173, 2007)",
        "url": "https://indianpediatrics.net/mar2007/173.pdf",
    },
    "NAPSE2024": {
        "title": "National Action Plan for Prevention and Control of Snakebite Envenoming (NAP-SE), MoHFW, 12 Mar 2024: helpline 15400 pilot",
        "url": "https://medicaldialogues.in/news/health/health-ministry-aims-to-halve-snakebite-deaths-by-2030-launches-national-action-plan-125813",
    },
    "ELIFE2020": {
        "title": "Suraweera et al., Trends in snakebite deaths in India 2000-2019, eLife 2020;9:e54076",
        "url": "https://elifesciences.org/articles/54076",
    },
    "EMS": {
        "title": "108 free emergency ambulance (National Health Mission) and 112 (Emergency Response Support System)",
        "url": "https://nhm.gov.in/",
    },
}

# States where helpline 15400 was piloted (NAP-SE, Mar 2024).
HELPLINE_15400_STATES = {"andhra pradesh", "assam", "delhi", "madhya pradesh", "puducherry"}

# id -> {en, hi, src}
ITEMS = {
    # ---- DO, in order of priority -------------------------------------------------
    "call_108": {
        "en": "Call 108 for a free ambulance now (or 112). Do not wait for pain or swelling to start.",
        "hi": "अभी 108 पर फ़ोन करें, मुफ़्त एम्बुलेंस आएगी (या 112)। दर्द या सूजन शुरू होने का इंतज़ार न करें।",
        "src": "EMS",
    },
    "call_15400": {
        "en": "Your state has the snakebite helpline: call 15400 for guidance on the way.",
        "hi": "आपके राज्य में सर्पदंश हेल्पलाइन है: रास्ते में मदद के लिए 15400 पर फ़ोन करें।",
        "src": "NAPSE2024",
    },
    "go_hospital": {
        "en": "Go straight to the nearest government hospital that has anti-snake venom (ASV), usually a district hospital or CHC. Only antivenom treats a venomous bite.",
        "hi": "सीधे सबसे नज़दीकी सरकारी अस्पताल जाएँ जहाँ एंटी-स्नेक वेनम (ASV) हो, आमतौर पर ज़िला अस्पताल या CHC। ज़हरीले दंश का इलाज सिर्फ़ एंटीवेनम है।",
        "src": "STG2017",
        "page": 7,
    },
    "reassure": {
        "en": "Keep the person calm and lying still. About 7 in 10 snakebites are from non-venomous snakes, and antivenom works.",
        "hi": "व्यक्ति को शांत रखें और लिटा कर रखें। लगभग 10 में से 7 सर्पदंश बिना ज़हर वाले साँपों के होते हैं, और एंटीवेनम असर करता है।",
        "src": "STG2017",
        "page": 7,
    },
    "immobilise": {
        "en": "Keep the bitten arm or leg still, like a broken bone: a loose splint or sling. Do not tie it tight or press on it.",
        "hi": "काटे गए हाथ या पैर को टूटी हड्डी की तरह स्थिर रखें: ढीली खपच्ची या झोली। कसकर न बाँधें, न दबाएँ।",
        "src": "STG2017",
        "page": 8,
    },
    "no_walk": {
        "en": "Do not let them walk, run or drive. Carry them or take a vehicle.",
        "hi": "उन्हें चलने, दौड़ने या गाड़ी चलाने न दें। उठाकर ले जाएँ या वाहन से ले जाएँ।",
        "src": "STG2017",
        "page": 8,
    },
    "remove_tight": {
        "en": "Take off rings, bangles, anklets, watch, shoes and tight clothes near the bite now. Swelling can make them cut off the blood.",
        "hi": "दंश के पास की अंगूठी, चूड़ियाँ, पायल, घड़ी, जूते और तंग कपड़े अभी उतार दें। सूजन आने पर ये खून रोक सकते हैं।",
        "src": "STG2017",
        "page": 8,
    },
    "nil_by_mouth": {
        "en": "Give nothing to eat or drink, no alcohol, and no aspirin or painkillers like ibuprofen, until a doctor sees them.",
        "hi": "डॉक्टर के देखने तक कुछ खाने-पीने को न दें, शराब नहीं, और एस्पिरिन या आइबुप्रोफ़ेन जैसी दर्द की दवा नहीं।",
        "src": "STG2017",
        "page": 8,
    },
    "recovery_position": {
        "en": "If they are vomiting, drowsy or unconscious, lay them on their side (recovery position) and keep the mouth and airway clear.",
        "hi": "अगर उल्टी हो रही है, नींद जैसी हालत है या बेहोश हैं, तो करवट लिटाएँ (रिकवरी पोज़िशन) और मुँह व साँस का रास्ता साफ़ रखें।",
        "src": "STG2017",
        "page": 8,
    },
    "note_time": {
        "en": "Note the time of the bite. Tell the doctor the time and every new symptom, such as drooping eyelids.",
        "hi": "दंश का समय याद रखें। डॉक्टर को समय और हर नया लक्षण बताएँ, जैसे पलकें झुकना।",
        "src": "NP2007",
    },
    "stay_24h": {
        "en": "Even if they feel fine, they must stay under observation in hospital for 24 hours. A krait bite can cause paralysis hours later with almost no pain.",
        "hi": "ठीक लगें तब भी, अस्पताल में 24 घंटे निगरानी में रहना ज़रूरी है। करैत के दंश से घंटों बाद लकवा हो सकता है, लगभग बिना दर्द के।",
        "src": "STG2017",
        "page": 10,
    },
    # ---- DON'T --------------------------------------------------------------------
    "dont_tourniquet": {
        "en": "Do NOT tie a rope, string or cloth tightly. Tourniquets do not stop venom and can kill the limb (gangrene).",
        "hi": "रस्सी, धागा या कपड़ा कसकर न बाँधें। इससे ज़हर नहीं रुकता और हाथ-पैर सड़ सकता है (गैंग्रीन)।",
        "src": "STG2017",
        "page": 9,
    },
    "dont_cut_suck": {
        "en": "Do NOT cut, suck, burn, rub, massage or wash the bite. It does not remove venom and causes bleeding and infection.",
        "hi": "दंश को न काटें, न चूसें, न जलाएँ, न रगड़ें, न मालिश करें, न धोएँ। इससे ज़हर नहीं निकलता, खून बहता है और संक्रमण होता है।",
        "src": "STG2017",
        "page": 9,
    },
    "dont_healer": {
        "en": "Do NOT go to an ojha or healer, or use jhaad-phoonk, black stone, herbs or pastes. They have no proven benefit and lose the time that saves lives.",
        "hi": "ओझा या झाड़-फूँक वाले के पास न जाएँ, काला पत्थर, जड़ी-बूटी या लेप न लगाएँ। इनका कोई फ़ायदा साबित नहीं है और जान बचाने वाला समय बर्बाद होता है।",
        "src": "STG2017",
        "page": 8,
    },
    "dont_catch": {
        "en": "Do NOT try to catch or kill the snake, and do not waste time searching for it.",
        "hi": "साँप को पकड़ने या मारने की कोशिश न करें, और उसे ढूँढने में समय न गँवाएँ।",
        "src": "STG2017",
        "page": 8,
    },
    # ---- corrections for things already done -------------------------------------
    "fix_tourniquet": {
        "en": "A band was already tied: do not tighten it or add more. Go now and tell the doctor about it; at the hospital they remove it safely.",
        "hi": "पहले से बंधन बाँधा गया है: इसे और कसें नहीं, और न बाँधें। अभी चलें और डॉक्टर को बताएँ; अस्पताल में वे इसे सुरक्षित तरीके से खोलेंगे।",
        "src": "NP2007",
    },
    "fix_cut": {
        "en": "The bite was cut or sucked: do not do it again. Cover it loosely with a clean cloth and tell the doctor.",
        "hi": "दंश को काटा या चूसा गया: दोबारा न करें। साफ़ कपड़े से ढीला ढकें और डॉक्टर को बताएँ।",
        "src": "STG2017",
        "page": 9,
    },
    "fix_healer": {
        "en": "Leave the healer and go to the hospital now. Tell the doctor exactly what was applied or given; it can confuse the symptoms.",
        "hi": "ओझा/वैद्य के पास से अभी अस्पताल चलें। डॉक्टर को ठीक-ठीक बताएँ कि क्या लगाया या खिलाया गया; इससे लक्षण भ्रमित हो सकते हैं।",
        "src": "STG2017",
        "page": 8,
    },
    "fix_ate": {
        "en": "Something was already given by mouth: give nothing more, and tell the doctor what it was.",
        "hi": "मुँह से पहले ही कुछ दिया गया: अब और कुछ न दें, और डॉक्टर को बताएँ कि क्या दिया।",
        "src": "STG2017",
        "page": 8,
    },
    "fix_walked": {
        "en": "They have been walking: stop now. Make them lie down and carry them.",
        "hi": "वे चल रहे थे: अभी रोकें। लिटाएँ और उठाकर ले जाएँ।",
        "src": "STG2017",
        "page": 8,
    },
    # ---- critical / special -------------------------------------------------------
    "critical_signs": {
        "en": "These are danger signs of venom acting on the body. Every minute counts: call 108 now and go to the nearest hospital with a doctor and ASV, even if it is not the closest one you know.",
        "hi": "ये शरीर में ज़हर के असर के ख़तरनाक लक्षण हैं। हर मिनट क़ीमती है: अभी 108 पर फ़ोन करें और ऐसे नज़दीकी अस्पताल जाएँ जहाँ डॉक्टर और ASV हो।",
        "src": "STG2017",
        "page": 20,
    },
    "suspect_krait": {
        "en": "This could be a krait bite even with no wound: kraits bite people sleeping on the floor at night, often painlessly. Stomach pain, vomiting, drooping eyelids or weakness in the morning need hospital NOW.",
        "hi": "बिना घाव के भी यह करैत का दंश हो सकता है: करैत रात में ज़मीन पर सोए लोगों को अक्सर बिना दर्द के काटता है। सुबह पेट दर्द, उल्टी, पलकें झुकना या कमज़ोरी हो तो अभी अस्पताल जाएँ।",
        "src": "STG2017",
        "page": 17,
    },
    "unsure_treat_as_snake": {
        "en": "If you are not sure what bit them, treat it as a snakebite and go to the hospital. It is safer to be checked.",
        "hi": "अगर पक्का नहीं पता कि किसने काटा, तो इसे सर्पदंश मानें और अस्पताल जाएँ। जाँच करवाना ही सुरक्षित है।",
        "src": "STG2017",
        "page": 7,
    },
    "child_note": {
        "en": "Children get a bigger dose of venom for their size. Go immediately.",
        "hi": "बच्चों के छोटे शरीर में ज़हर का असर ज़्यादा होता है। तुरंत जाएँ।",
        "src": "STG2017",
    },
    "pregnant_note": {
        "en": "Pregnancy: go to a hospital that also has a gynaecologist if possible, but do not delay to find one.",
        "hi": "गर्भावस्था: हो सके तो ऐसे अस्पताल जाएँ जहाँ स्त्री-रोग डॉक्टर भी हों, पर इसके लिए देर न करें।",
        "src": "STG2017",
    },
    "late_note": {
        "en": "Many hours have passed, but antivenom can still help. Go now.",
        "hi": "कई घंटे बीत गए हैं, फिर भी एंटीवेनम मदद कर सकता है। अभी जाएँ।",
        "src": "STG2017",
    },
    # ---- out of scope -------------------------------------------------------------
    "other_bite": {
        "en": "Dansh only covers snakebite. For a dog, monkey or other animal bite, wash the wound with soap and running water for 15 minutes and go to a government hospital today for rabies vaccine. For a scorpion sting with severe pain, sweating or breathlessness, call 108.",
        "hi": "दंश सिर्फ़ सर्पदंश के लिए है। कुत्ते, बंदर या किसी जानवर के काटने पर घाव को साबुन और बहते पानी से 15 मिनट धोएँ और आज ही सरकारी अस्पताल में रेबीज़ का टीका लगवाएँ। बिच्छू के डंक में तेज़ दर्द, पसीना या साँस फूलने पर 108 पर फ़ोन करें।",
        "src": "EMS",
    },
    "off_topic": {
        "en": "Dansh only helps after a snakebite. Describe what happened, for example: 'snake bit my father on the leg 10 minutes ago'. For any other emergency call 112.",
        "hi": "दंश सिर्फ़ सर्पदंश के बाद मदद करता है। बताइए क्या हुआ, जैसे: 'पापा को 10 मिनट पहले पैर में साँप ने काटा'। किसी और आपात स्थिति में 112 पर फ़ोन करें।",
        "src": "EMS",
    },
    "self_harm": {
        "en": "If you or someone is thinking about self-harm, call Tele-MANAS 14416 (free, 24x7) or 112 now. You are not alone.",
        "hi": "अगर आप या कोई ख़ुद को नुकसान पहुँचाने की सोच रहा है, तो अभी Tele-MANAS 14416 (मुफ़्त, 24x7) या 112 पर फ़ोन करें। आप अकेले नहीं हैं।",
        "src": "EMS",
    },
    # ---- prevention ---------------------------------------------------------------
    "prevent_torch": {
        "en": "Carry a torch or phone light when walking at night, and wear closed shoes or boots in fields.",
        "hi": "रात में चलते समय टॉर्च या फ़ोन की लाइट रखें, और खेत में बंद जूते या गमबूट पहनें।",
        "src": "ELIFE2020",
    },
    "prevent_sleep": {
        "en": "Sleep on a cot, not on the floor, and use a mosquito net tucked in well. Kraits bite sleepers on the floor.",
        "hi": "ज़मीन पर नहीं, खाट पर सोएँ, और मच्छरदानी अच्छी तरह दबाकर लगाएँ। करैत ज़मीन पर सोने वालों को काटता है।",
        "src": "STG2017",
        "page": 17,
    },
    "prevent_hands": {
        "en": "Use a stick to check grass, wood piles and holes before putting your hands in. Keep the area around the house clear of rubbish and rats.",
        "hi": "घास, लकड़ी के ढेर और बिलों में हाथ डालने से पहले डंडे से जाँच लें। घर के आस-पास कूड़ा और चूहे न रहने दें।",
        "src": "ELIFE2020",
    },
}

# Red-flag symptom keys -> label shown back to the user ("we understood: ...")
RED_FLAGS = {
    "ptosis": {"en": "drooping eyelids or blurred/double vision", "hi": "पलकें झुकना या धुंधला/दोहरा दिखना"},
    "breathing": {"en": "difficulty breathing", "hi": "साँस लेने में तकलीफ़"},
    "speech_swallow": {"en": "trouble speaking or swallowing", "hi": "बोलने या निगलने में तकलीफ़"},
    "bleeding": {"en": "bleeding (gums, nose, urine, vomit)", "hi": "खून आना (मसूड़े, नाक, पेशाब, उल्टी)"},
    "unconscious": {"en": "drowsy, fainting or unconscious", "hi": "बेहोशी या बहुत नींद"},
    "weakness": {"en": "weakness or paralysis", "hi": "कमज़ोरी या लकवा"},
    "vomiting_abdominal": {"en": "vomiting or stomach pain", "hi": "उल्टी या पेट दर्द"},
}

# Yes/no follow-up questions the agent asks when a red flag is still unknown.
FOLLOW_UPS = [
    ("ptosis", {"en": "Are the eyelids drooping, or is vision blurred/double?", "hi": "क्या पलकें झुक रही हैं, या धुंधला/दोहरा दिख रहा है?"}),
    ("breathing", {"en": "Any difficulty breathing?", "hi": "क्या साँस लेने में तकलीफ़ है?"}),
    ("bleeding", {"en": "Any bleeding from gums, nose, or red/dark urine?", "hi": "क्या मसूड़ों, नाक से खून या लाल/काला पेशाब?"}),
    ("unconscious", {"en": "Is the person drowsy or hard to wake?", "hi": "क्या व्यक्ति बहुत सुस्त है या मुश्किल से जाग रहा है?"}),
]

UI = {
    "level_CRITICAL": {"en": "EMERGENCY: danger signs", "hi": "आपातकाल: ख़तरे के लक्षण"},
    "level_URGENT": {"en": "Snakebite: go to hospital now", "hi": "सर्पदंश: अभी अस्पताल जाएँ"},
    "level_POSSIBLE": {"en": "Possible snakebite: go to hospital now", "hi": "संभावित सर्पदंश: अभी अस्पताल जाएँ"},
    "level_INFO": {"en": "Staying safe from snakebite", "hi": "सर्पदंश से बचाव"},
    "level_OTHER": {"en": "Not a snakebite", "hi": "सर्पदंश नहीं"},
    "level_OFF_TOPIC": {"en": "Tell me what happened", "hi": "बताइए क्या हुआ"},
    "level_SUPPORT": {"en": "Please reach out now", "hi": "कृपया अभी संपर्क करें"},
}


def text(item_id: str, lang: str) -> str:
    item = ITEMS[item_id]
    return item.get(lang) or item["en"]


def cite(item_id: str) -> dict:
    item = ITEMS[item_id]
    src = SOURCES[item["src"]]
    out = {"key": item["src"], "title": src["title"], "url": src["url"]}
    if "page" in item:
        out["page"] = item["page"]
    return out
