# Verifier round 7: 3103d26 (previous b002768, base b557550)

Scratch: /tmp/chk8 (clone in repo/). No edits in /home/claude/dansh.

## 1. Test suite (/home/claude/dansh @ 3103d26)
```
222 passed in 10.71s
```

## 2. Cheating / gate check
- `git diff --stat b002768 3103d26 -- tests eval_cases eval_results app/content.py deploy LICENSE`: only tests/data/adversarial.json (+1589 lines).
- Corpus 992 -> 1294. Full-record multiset (json.dumps sort_keys): 0 removed, 302 added; 0 relabelled. vs base b557550: 0 removed, 746 added.
- Added labels: bite 170, crit 66, ctl 39, animal 27. All 216 round-6 held-out items are now in the corpus; the 28 "plain" ones were added as expect "bite" (judge(): bite = hospital plan required, so stricter-or-equal for the hospital requirement; the URGENT-not-CRITICAL goal is not asserted anywhere).
- No tests/*.py changed. Note: the soft false-alarm bound `max(10, n_ctl // 4)` grows as ctl items are added (structural, not a loosened assertion).
## 3-4. Fresh held-out set (/tmp/chk8/heldout7.json, sha256 11020a7a..., script scripts/make_heldout7.py; labels fixed before any run)

224 messages: 110 bite, 45 crit (38 realistic + 2 arguable + 5 deliberate gap probes marked `probe`), 27 plain (snake named, no danger sign; expect URGENT), 27 ctl (3 arguable), 15 animal. Novelty: 0 exact/substring hits vs repo tests/, eval_cases/, loop/, corpus and /tmp/chk*/heldout*.json, grid*.json (9 initial substring hits replaced before any run). Written as real WhatsApp users type (Hinglish, typos, Devanagari, fragments); crit items are ordinary frightened-relative phrasings, not adversarial synonyms.

| label (n) | outcome | 3103d26 (all / non-arg) | b002768 | b557550 |
|---|---|---|---|---|
| bite (110) | FALSE_SAFE | **0 / 0** | 1 / 1 | 1 / 1 |
| crit (45) | FALSE_SAFE | 0 / 0 | 0 / 0 | 0 / 0 |
| crit (45) | UNDER | **2 / 1** (1 arguable) | 3 / 2 | 6 / 5 |
| crit probes (5, in the 45) | UNDER | 0 | 0 | 0 |
| plain (27) | FALSE_SAFE | 0 | 0 | 0 |
| plain (27) | OVER (CRITICAL) | **0 / 0** (27/27 URGENT) | 0 | 0 |
| ctl (27) | FALSE_ALARM | 14 / 12 | 14 / 12 | 12 / 10 |
| animal (15) | ANIMAL_MISROUTE | 5 / 5 | 4 / 4 | 3 / 3 |

Cross-checked with tests/test_adversarial.judge (plain judged as "bite"): identical.
Bite levels at 3103d26: URGENT 80, POSSIBLE 29, CRITICAL 1 (`saanp kaata ungli me, khoon thoda nikla` -> ['bleeding'], acceptable).

### Every FALSE_SAFE at 3103d26: none.
(b002768 and b557550: `do chhote chhed hain pair me aur sujan` [OFF_TOPIC] trace=['R3 no snake/bite recognised -> ask'] - fixed by the new "chhed" UNKNOWN word.)

### Every UNDER at 3103d26 (2)
- - [URGENT] `snake bite, everything looks double to him` trace=['R5 snake named, no danger signs yet -> URGENT']  (also at b002768, b557550)
- A [URGENT] `bitten by snake, legs are numb and he can't walk` trace=['R5 snake named, no danger signs yet -> URGENT']  (also at b002768, b557550)

Fixed vs b002768: `bhai ki aawaz nahi nikal rahi saap kaatne ke baad` (now CRITICAL).

### plain -> CRITICAL at 3103d26: 0 of 27 (b002768 0, b557550 0).

### False alarms / misroutes at 3103d26 (tolerated)
- FALSE_ALARM [URGENT]: `saap dikha aangan me, kisi ko kaata nahi, kaise bhagaye`, `ghar ke aas paas saap na aaye uske liye kya lagaye`, `kaunsa saap zehrila hota hai`, `saap ka video bhejo`, `snake catcher ka number chahiye`, `kya sabhi saap zehrile hote hain`, `saanp ka sapna aaya raat ko, kya matlab hai`, `snake ka chamda mila chhat pe`, `a cobra was sitting near the gate this morning, it went away`, `saap ko maar diya lathi se, sab theek hai`, `snake wala gaana bajao`, (A) `I dreamt a snake bit me`, (A) `our dog killed a snake in the garden, dog is fine`; [POSSIBLE] `biting my nails is a bad habit`.
  Note: Hinglish snake questions without "?" ("kaunsa saap zehrila hota hai") get the full URGENT plan.
- ANIMAL_MISROUTE [POSSIBLE]: `chhat pe bandar aaya aur usne didi ke haath pe kaat liya`, `billi ne nakhoon maar diya aur kaat liya` (new vs b002768), `bichhoo ne dank maara ungli pe`, `ghode ne kaata`, `kutte ke kaatne ke baad kya karein`.

## 5. Regression hunt (labels fixed in scripts before each run)
Grids: grid7.json (109, sha256 c1b6b500...), grid7b.json (30, new FLAG_WORDS / UNKNOWN / PRICK words, 2187b5a1...), grid7c.json (18, effect of removing R4b SYSTEMIC, 12a310f4...), grid7d.json (16, round-6 false-safe class with new wording, 88f3b1ae...). Total 173.

| grid / group | n | 3103d26 non-ok | b002768 non-ok | b557550 non-ok |
|---|---|---|---|---|
| grid7 bite (a,b,c,g) | 23 | 0 | FS 2 (0 non-arg) | FS 3 (1) |
| grid7 crit (c,d,e,f) | 38 | UNDER 2 (2) | UNDER 2 (2) | UNDER 4 (4) |
| grid7 plain (c,d,e,f) | 16 | OVER 5 (2) | OVER 13 (7) | OVER 11 (6) |
| grid7 ctl (a,b) | 21 | FA 17 (12) | FA 15 (10) | FA 14 (9) |
| grid7 animal (g,h) | 11 | MIS 2 (0) | 0 | MIS 1 (1) |
| grid7b plain (new words) | 20 | **OVER 16 (10)** | OVER 3 (2) | OVER 1 (1) |
| grid7b ctl | 8 | FA 5 (3) | FA 1 (1) | FA 1 (1) |
| grid7b crit | 2 | UNDER 1 (1) | 0 | UNDER 1 (1) |
| grid7c crit (systemic) | 18 | UNDER 2 (1) | 0 | UNDER 6 (5) |
| grid7d bite (contact + "?") | 16 | **0** | FS 3 (3) | FS 3 (3) |

### False safes in all grids at 3103d26: none (0/55 bite).

### Non-arguable crit UNDER in grids at 3103d26 (4)
- `saanp ne kaata, papa call karne pe jawab nahi de rahe` [URGENT] trace=['R5 snake named, no danger signs yet -> URGENT'] (same at b002768, base)
- `snake bite, his urine is not normal, it is red` [URGENT] trace=['R5 ...'] (same at b002768, base) - "is not normal" sits between "urine" and "red"; FLAG_RE window/negation miss
- `snake bite, he keeps falling asleep` [URGENT] trace=['R5 ...'] **regression: CRITICAL at b002768 (via the removed R4b SYSTEMIC)**
- `snake bit my son and he keeps falling asleep in my arms` [URGENT] **same regression**
- (A) `snake bit him, he is lethargic` [URGENT] (CRITICAL at b002768)

### Mechanism notes
- **first_person / sighting_only (snake_mention_only)**: works. Every first-person contact question I wrote reaches a hospital plan (`snake was on my bed when i woke up?`, `a snake bumped my foot?`, `I touched a snake, will I be okay?`, `saap mere dupatte me tha, kya karu?`, `snake was under my pillow this morning, should i be worried?`; the last three were INFO false safes at b002768). Pure first-person sightings/prevention (`i saw a snake near my house, what should i do?`, `maine saap dekha khet me, kya karu?`, `how do i keep snakes off my farm?`) stay INFO. Side effect: `i want to know which snakes are in my area` -> URGENT (also at b002768).
- **SNAKE_CONTACT_RE**: does give false contact on the new words, false alarms only: `i'm wearing boots, how to avoid snakes in the field?` (INFO -> URGENT, new), `jeb me phone hai, saap ka photo bhej raha hu` (INFO -> URGENT, new). `sitting at home reading about snakes` is URGENT, but it already was at b002768 and base (not caused by the new "sitting").
- **NOT_A_SIGN_RE**: works as intended: `network weak`, `hospital phone nahi utha raha`, `can't stand the pain/it` now URGENT (were CRITICAL). Does not hide real signs: `he is weak and the network is weak too`, `she is not responding, the phone signal is weak`, `network kamzor hai, papa bhi bahut kamzor lag rahe`, `he is not answering when we call his name` all CRITICAL. Hinglish `jawab nahi de rahe` (unresponsive) is not a listed sign (pre-existing gap).
- **_flag_re_hit negation**: `he is not breathing`, `no breathing at all`, `not breathing properly`, `isn't breathing well`, `not able to breathe`, `breathing is not normal`, `not breathing normally`, `eyes are not opening`, `was not responding for a while`, `not bleeding but she is vomiting` -> all CRITICAL. `breathing is ok`, `breathing normal`, `he is not vomiting`, `no vomiting, no bleeding` -> URGENT (fixed). `he is not weak` (A) still CRITICAL.
- **QUESTION_CLAUSE**: `is his breathing ok?` is still treated as a question (not a denial), so the flag stays and it is CRITICAL (over-triage, same as before; safe). `he is not breathing` / `and now he is not breathing` still flag. `is it bad that he can't open his eyes?`, `is it normal that he is so sleepy?`, `kya ye normal hai ki aankhen nahi khul rahi?`, `breathing is ok but he vomited twice` all CRITICAL.
- **PRESENCE_TYPE "not"**: `it is not bleeding`, `not vomiting yet`, `no longer vomiting` -> URGENT (fixed). `bleeding is not stopping`, `wound is not stopping bleeding`, `can not stop vomiting`, `has not stopped vomiting`, `not vomiting anymore but he is very sleepy` -> CRITICAL (no false denial found).
- **Hinglish rat**: `rat ko saap ne kaata`, `rat me kuch kaat gaya pair pe`, `rat 2 baje bacche ko kuch kaata`, `kal rat ko bete ko kisi ne kaata`, `rat bite hua, haath suj gaya` -> hospital; `rat ne kaat liya ungli pe din me`, `mujhe rat ne kaata`, `chuhe ne kaata ungli pe`, `ek rat ne bachhe ko kaata, din me, kitchen me`, `rat bit my finger in the kitchen at noon` -> OTHER. Works.
- **R1f with swelling**: `a rat bit my hand in the shop, it's a bit swollen` and `a lizard bit my finger, it is swollen` -> POSSIBLE (misroute, arguable, tolerated). Dog/monkey/bee + swelling stay OTHER (LOOKALIKE = rat, lizard, insect only).
- **unsure_treat_as_snake note**: present on INFO when a snake is named and on OFF_TOPIC when bite/snake/contact is seen. It also appears on `snake plant care tips` and `snakes and ladders rules` INFO plans (odd wording there, harmless). No hospital item is added, so it does not change any level.
- **New FLAG_WORDS (many copied from round-6 crit phrasings) over-match ordinary plain-bite wording**: grid7b shows plain->CRITICAL 16/20 (10 non-arguable), 13 of them new in 3103d26:
  - `neend me` -> unconscious: `beta neend me tha jab saap ne kaata` (the classic "asleep when bitten" krait story);
  - `so ja raha` -> unconscious: `bachha so ja raha tha zameen pe, tab saap ne kaata` (A);
  - `andhera` -> unconscious: `raat ko andhera tha, saap ne pair pe kaata`;
  - `shaking` -> unconscious: `he is shaking with fear`, `he's crying and shaking` (A);
  - `sit up` -> weakness: `he can sit up and talk fine`;
  - `reddish` / `bruise` -> bleeding: `the area around the bite is reddish`, `bite mark looks like a bruise` (A);
  - `gir pada` -> unconscious: `saap ped se gir pada aur bhai ko kaat liya` (the snake fell);
  - `stay awake` -> unconscious: `do we need to stay awake all night with him?`;
  - `been sick` -> vomiting: `he has been sick with sugar for years`;
  - `bluish` -> breathing (A), `gave way` -> weakness (A).
  These are over-triage (still a hospital plan), so not safety failures; but they contradict the quality goal and are word-list patches of the previous verifier's exact items.
- **New UNKNOWN / PRICK words** give new false alarms: `sharp pain in my back since morning` -> POSSIBLE, `kisi ne mujhe galat number diya` -> POSSIBLE, `diwar me chhed hai, saap aa sakta hai kya?` -> URGENT, (A) `the dog jabbed my leg with his nose` -> POSSIBLE.

## 6. BENCHMARK-RESULTS.md "Audit-found inputs"
- "1,294 messages ... 1,246/1,294 as labelled, 0 false safes, 0 under-triage; all 48 differences are over-triage": **reproduced** (1246 ok, 41 FALSE_ALARM, 7 ANIMAL_MISROUTE, 0 FS, 0 UNDER). The soft false-alarm bound is 41 <= max(10, 172//4 = 43), close to the limit.
- Round-6 numbers (12 non-arguable FS vs 20 at base, 44/51 UNDER, 21/28 plain CRITICAL): **match** verify-round-6.md.
- "the catch-all ... was removed": true (SYSTEMIC_RE, R4b and Facts.systemic are gone). It does not say that this also loses `he keeps falling asleep` / `he is lethargic`, which b002768 caught.
- "The misses were people touching a snake ... Now a snake with I/my/me or a touch/clothing word is an event": true on my probes (grid7d 0/16 FS vs 3 at b002768). It is partial as a summary: round 6 also had 3 no-bite-word OFF_TOPIC misses (`do chhed`, `sharp jab`, `kuch ne maara`), which were handled with new UNKNOWN/PRICK words.
- "every prevention or 'describe what happened' reply that mentions a snake or a bite also says ... treat it as a snakebite ... every reply shows 108": **true** on my probes (INFO calls ['108']; OFF_TOPIC and OTHER calls ['112','108']/['108','112']).
- "It does not show that every unseen phrasing is caught": accurate, honest framing.

## Evidence summary
- Tests: 222 passed. Gate: protected paths unchanged except corpus additions (992 -> 1294; 0 removed, 0 relabelled; round-6 plain items added as "bite"). No assertion loosened.
- Corpus claim reproduces (1246/1294, 0 FS, 0 UNDER).
- Fresh held-out (224, realistic WhatsApp style) at 3103d26 / b002768 / b557550:
  - bite FALSE_SAFE: **0** / 1 / 1;
  - crit UNDER non-arguable: **1** / 2 / 5 (`snake bite, everything looks double to him`; pre-existing); 5/5 gap probes caught;
  - plain->CRITICAL: **0/27** / 0 / 0;
  - ctl FA 14 / 14 / 12; animal misroute 5 / 4 / 3.
- Regression grids (173): 0 false safes (0/55 bite; the round-6 contact-question class is fixed: 0/16 vs 3/16). 4 non-arguable crit UNDER, 2 pre-existing and 2 a regression from removing R4b (`keeps falling asleep`). The main regression is over-triage: the new FLAG_WORDS make ordinary plain-bite phrasings CRITICAL (`neend me tha jab saap ne kaata`, `andhera`, `shaking`, `sit up`, `reddish`, `gir pada`, `been sick`), 10 non-arguable in a 20-item targeted grid, plus a few new false alarms (`wearing`, `jeb`, `sharp`, `kisi ne`, `chhed`).
- Decision rule on the held-out set: non-arguable bite FS = 0; non-arguable realistic crit UNDER = 1 (<= 3); plain->CRITICAL = 0 (<= 5). Every reject condition is clear. Recommended follow-ups (not blocking): scope `neend me`/`so ja raha`/`andhera`/`shaking`/`sit up`/`reddish`/`gir pada`/`been sick` to post-bite patient states; add `keeps falling asleep`/`lethargic`/`jawab nahi de rahe`; make the urine pattern tolerate "is not normal, it is red".

VERDICT: APPROVE
