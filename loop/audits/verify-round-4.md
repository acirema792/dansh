# Checker verdict, round 4: 931552f "fix(V4)"

**Verdict: REJECT.**

- **Scope:** 931552f, on top of cf98d6e (the commit that adds the corpus). The parent used for comparison is cf98d6e.
- **No edits** were made in /home/claude/dansh. Scratch is /tmp/chk5:
  - Clean clone: `repo/`. Parent worktree: `parent/`.
  - Held-out set: `heldout.json` (175 messages, expect + message), and `heldout_full.json` (adds kind and arguable flags).
  - Scripts: `scripts/make_heldout.py` (labels fixed before any run), `scripts/run_heldout.py`, `scripts/grid.py`.
  - Outputs: `heldout_out.txt` (HEAD), `heldout_parent.txt`, `grid_head.txt`, `grid_parent.txt`, `x_*` (evals).

## Why REJECT

1. **931552f adds 20 new false safes and fixes none** on fresh messages. On the same 175-message set it has 30 false safes; its parent cf98d6e has 10. Every false safe at the parent is still a false safe at HEAD.
2. **A 52-message minimal-pair grid built around the new rules gives 48/52 false safe at HEAD and 8/52 at the parent.** The causes are new code in this commit:
   - The new OTHER animal words: cow, buffalo, goat, pig, bat, spider, horse, mouse and others.
   - New SELF_BITE triggers: "bit into", "teething", "katta hai".
   - The new `snake_mention_only` INFO rule.
   - The narrowed safety net (`real_cue`).
3. **Under-triage is unchanged:** 32 of 52 danger-sign messages fall short of CRITICAL (33 at the parent). The danger-sign vocabulary is still built from exact phrases.
4. **Round-3 required item 3 was not done.** OTHER still suppresses the net whenever an animal word appears anywhere in the message, not only when the animal is the stated biter. `_explicit_animal_biter` (parser.py:393) is defined but never called. The commit made this worse by adding farm animals and "bat" to OTHER.
5. **The safety invariant in loop-constraints.md is broken:** "no change may make any possible-snakebite input produce advice other than go to hospital". The commit traded false safes for fewer false alarms (16→9) and fewer animal misroutes (5→0).
6. **The headline "25 -> 0" holds only on the round-3 set it was tuned against.** On that set I also get 0/73 bite or crit messages false safe, and 0/63 on the round-3 grid. But the grid is not in the tests (0 of its 63 messages are in the corpus), and fresh messages fail at the rates above.

## 1. Clean clone, tests

```
git clone -q https://github.com/acirema792/dansh /tmp/chk5/repo   # HEAD 931552f
python3 -m pytest -q tests 2>&1 | tail -3
........................................................................ [ 99%]
..                                                                       [100%]
218 passed in 7.06s
```
The corpus is now committed, so the suite runs on a clean clone. That fixes round-3 item 1.

## 2. Held-out hunt (175 new messages, 0 overlap with tests/, eval_cases/, loop/audits/)

- **Novelty:** checked by case-insensitive exact substring against every file in tests/ (including adversarial.json), eval_cases/ and loop/audits/. One collision was found and reworded before any run.
- **Labels:** written in make_heldout.py before any run. 4 labels are marked arguable.
- **Mix:** 68 realistic (39%) and 107 adversarial (61%). The adversarial messages are white-box, written against parser.py.

| Kind / label | n | ok | FALSE_SAFE | UNDER | FALSE_ALARM | ANIMAL_MISROUTE |
|---|---|---|---|---|---|---|
| realistic bite | 32 | 27 | **5** | | | |
| realistic crit | 22 | 12 | 0 | **10** | | |
| realistic ctl | 7 | 7 | | | 0 | |
| realistic animal | 7 | 7 | | | | 0 |
| adversarial bite | 46 | 21 | **25** | | | |
| adversarial crit | 30 | 8 | 0 | **22** | | |
| adversarial ctl | 23 | 14 | | | 9 | |
| adversarial animal | 8 | 8 | | | | 0 |
| **Total** | 175 | 104 | **30 of 130** | **32 of 52** | 9 of 30 | 0 of 15 |

The same set at the parent cf98d6e gives FALSE_SAFE 10, UNDER 33, FALSE_ALARM 16 and ANIMAL_MISROUTE 5.

### Every FALSE_SAFE, verbatim (level reached in brackets; * = new in 931552f, a = arguable label)

Realistic:
1. `kal rat khet me papa ke pair me kaat liya, sujan hai` (OTHER, rat). "rat" is a typo of "raat" (night).
2. `rat 2 baje bete ke pair me kaata, bahut dard ho raha` (OTHER, rat)
3. * `chacha ko keede ne das liya pair pe, bahut jalan` (OFF_TOPIC)
4. * `bitten while milking the cow early morning, father's foot is swelling fast` (OTHER)
5. `my daughter was bitten near the ant hill behind our house, leg swelling` (OTHER, ant)

Adversarial:
6. * `my wife was bitten on the wrist while gathering cow dung, it is swelling` (OTHER)
7. * `my father was bitten while tying the buffalo in the shed at night, leg swollen` (OTHER)
8. * `got bitten while picking up the cricket bat from the long grass, finger is swelling` (OTHER)
9. * `my son was bitten while grazing the goat near the canal, he is crying with pain` (OTHER)
10. * `bitten on the ankle near the pig sty this evening, ankle painful and swollen` (OTHER)
11. *a `bitten while sweeping the spider webs in the store room, hand swelling` (OTHER)
12. `rat main sote waqt haath pe kaata, haath sooj gaya` (OTHER, rat)
13. `rat ki 11 baje bachi ko pair pe kaata, ro rahi hai` (OTHER, rat)
14. `aaj rat khet se aate waqt pair me kaata, jalan ho rahi` (OTHER, rat)
15. *a `my mother was bitten on the toe while setting the mouse trap in the grain store at night, toe is swollen` (OTHER, rat)
16. * `something bit into her heel while she was cutting grass` (OFF_TOPIC)
17. * `something bit into my son's toe at night while he slept on the floor, he is crying` (OFF_TOPIC)
18. * `my baby is teething, but last night something bit her finger while she slept on the floor and she keeps crying` (OFF_TOPIC)
19. * `a creature bit into his calf in the paddy field` (OFF_TOPIC)
20. * `saanp ne maara, kya kare` (INFO)
21. * `snake hit him, what should we do` (INFO)
22. *a `cobra spat in his eyes, what to do` (INFO)
23. * `a snake fell on her from the roof while she was sleeping, what do we do` (INFO)
24. * `naag ne chhu liya, kya karein` (INFO)
25. * `snake wrapped around him in the field, what now` (INFO)
26. *a `saanp ne jhapat mari, kya karu` (INFO)
27. `my son got bitted on leg` (OFF_TOPIC)
28. `snakbit on foot hlp` (OFF_TOPIC). "snakbite" is in the SNAKE list, "snakbit" is not.
29. `keede ne das liya bachi ko raat me` (OFF_TOPIC)
30. `a thing slithered over my son's foot in the field and now there is a red mark` (OFF_TOPIC)

Without the 4 arguable labels, 26 false safes remain, 16 of them new in 931552f.

### Every UNDER, verbatim (all reach URGENT unless noted)

Realistic:
1. `saanp ne kaata tha ab aankhe nhi khul rhi`
2. `snake bit my brother, he threw up twice`
3. `सांप के काटने के बाद उल्टियां हो रही हैं`
4. `saanp kaatne ke baad mamaji ki gardan nahi uth rahi`
5. `my grandmother was bitten by a snake and now she can't talk properly`
6. `cobra bite, his eyes are rolling and he's not answering`
7. `सांप ने काटा, वो नहीं उठ रहा`
8. `snake bitten 2 hours ago, urine has become dark red`
9. `बच्चे को सांप ने काटा, उसके हाथ पैर ढीले पड़ गए`
10. `saap ne kata, ab haath pair kaam nahi kar rahe`

Adversarial:

11. `snake bite, he is vomitting`
12. `saanp ne kaata, ultiyan ho rahi`
13. `cobra bit my dad, he can't talk properly`
14. `snake bit her, now she is mumbling, words not clear`
15. `krait bite, he is not able to keep his head up`
16. `saanp ne kaata, sir nahi uth raha`
17. `सांप ने काटा, वो नहीं जाग रहा`
18. `सांप ने काटा, दौरे पड़ रहे हैं`
19. `सांप ने काटा, आंख नहीं खोल पा रहा`
20. `snake bite, he is seeing two of everything`
21. `snake bit him, he is convulsing`
22. `snake bit grandpa, he's breathin very slow`
23. `saanp ne kata, neend aa rhi bahut`
24. `saap ne kata, peshab lal aa raha`
25. `snake bite, her pee has turned brown`
26. `snake bit him, his throat is closing up`
27. `snake bit, chest feels heavy and he is panting`
28. `saanp ne kata, awaz badal gayi`
29. `sanp ne kata, nigal nhi pa rha`
30. `pair me kuch kaata khet me, ab bat nahi kar pa raha` (POSSIBLE). Here "bat" (a typo of "baat", talk) is also read as an animal.
31. `my old father, 70, bitten by snake, now he is very confused and talking nonsense`
32. `the snake bit my son, he's very pale, cold and sweaty and not making sense`

The UNDER cases have common causes:
- **Word-final boundaries.** "ulti" does not match "ultiyan", and "vomit" does not match "vomitting".
- **Devanagari inflections.** "उल्टी" does not match "उल्टियां", and "ढीला" does not match "ढीले". Hindi word order defeats the list too: "नहीं उठ" and "नहीं जाग" are missed, but "उठ नहीं" is caught.
- **SMS spellings.** "nhi", "rhi" and "rha" are not matched.
- **Common English verbs are missing:** "threw up", "talk", "convulsing", "panting" and "confused".

### False alarms (9; tolerated by design, listed for completeness)

- `I stepped on a nail at the construction site, tetanus shot needed?` (new: "nail" was moved from THORN to BODY_PARTS)
- `needle pricked my finger while sewing, it hurts a little`
- `sanp seedhi khelna hai`
- `cobra kai season 6 kab aayega`
- `python code bites me every time lol`
- `love bite on my neck, how to hide it`
- `the cold wind bites at night in the fields`
- `a snake crossed the path in front of us but did not bite anyone, we are all fine`
- `saanp dikha par kaata nahi, sab theek hai`

### Regression grid (scripts/grid.py, all labelled bite)

| Pattern | HEAD 931552f | parent cf98d6e |
|---|---|---|
| bite + animal word as context ("while feeding the cow", "near the ant hill") | 28/28 FS | 8/28 |
| SELF_BITE trigger + third-party bite ("something bit into", "teething") | 5/5 FS | 0/5 |
| snake + non-bite verb + "what should we do / kya karein" | 12/14 FS | 0/14 |
| body part + symptom, unlisted bite verb ("das liya") | 3/5 FS | 0/5 |
| **Total** | **48/52** | **8/52** |

## 3. Code review: rules outside can_suppress() that remove a bite signal or demote a level

1. **parser.py:417-421 + :475 + :480, protocol.py:63 and :91-98 (OTHER animal).**
   - Any OTHER word anywhere in the text sets `other_animal`. "rat" is matched as a whole word, so "raat" typos like "kal rat" or "rat main" count; ANIMAL_NOT_RE (parser.py:334) covers only "rat ko/me/mein/bhar/ke".
   - With no doubt word, this sets `explicit_other`, which disables the safety net (parser.py:480).
   - It also removes bite context (protocol.py:63: `f.bite and not f.other_animal`). R1 (protocol.py:91-98) then returns OTHER, even with an explicit "was bitten" and swelling.
   - The commit adds cow, buffalo, goat, pig, bat, horse, donkey, camel, spider, parrot and mouse (parser.py:105, 110-111). That widens this demotion path.
   - `_explicit_animal_biter` (parser.py:393), which would restrict this to a stated biter, is never called.
2. **protocol.py:77-82 (LOOKALIKE).** The rescue for rat or lizard needs `flags`, meaning a red flag. Swelling, pain and marks do not count, so "rat bit at night, foot swollen" stays OTHER.
3. **parser.py:444-447 (SELF_BITE).**
   - It sets `bite=False` and `unknown_bite=False`. It checks only snake, flag_hit, swelling and victim; night, outdoor, pain, crying, doubt and urgency are ignored.
   - parser.py:481 and :490 add `not SELF_BITE.search(text)`, which disables the safety net completely.
   - The commit added the triggers "bit into", "teething", "दांत निकल", "kaatta/katta hai" and "bites everything" (parser.py:385-386).
4. **parser.py:492-498 + protocol.py:103-109 (snake_mention_only → INFO).** This is a new demotion of a message that names a snake.
   - It fires on any message containing an INFO_WORD, and INFO_WORDS includes "what", "how", "kya", "kaise", "keep" and "show".
   - It does not check pronoun victims (him, her), outdoor settings, or contact verbs (hit, fell on, spat, wrapped around, "chhu liya", "maara").
5. **parser.py:478-479 (real_cue).** The safety net now needs a bite word or prick word, or outdoor plus a body part. "body part + symptom" no longer raises POSSIBLE, so "keede ne das liya pair pe, bahut jalan" regressed to OFF_TOPIC. This narrows the raise rather than removing a signal, but it is outside can_suppress.
6. **Guarded by can_suppress, no false safe found:**
   - HUMAN_BITER (parser.py:450)
   - INJURY marks (453)
   - THORN (458; now also blocked by an explicit bite word)
   - weak-only general question (466)
   - generic_question (469)
7. **Pre-existing:**
   - BIT_IDIOM and SUCKED_BLOOD text rewrites (parser.py:407, 409).
   - HI_NEG_AFTER denies presence signs and swelling when "nahi" follows ("sujan nahi gayi").
   - Fixed in this commit: `never` was removed from NEG_BEFORE (parser.py:244).
8. **Hygiene:** protocol.py:87 `if False:` is dead code left from the old R1d.

BENCHMARK-RESULTS.md:39 says "The current design has one guard (`can_suppress`) and a safety net, so doubt always resolves to the hospital". Items 1, 3 and 4 show that this is false.

## 4. Eval sets (clean clone, `DANSH_DB=/tmp/chk5/db/dansh.db uvicorn :8092`, /api/health commit 931552f; server stopped)

| Eval set | Bite cases sent to hospital | False safe | Cases passed | Under | Over | Controls correct |
|---|---|---|---|---|---|---|
| cases.yaml | 18/18 | 0 | 22/22 | 0 | 0 | 4/4 |
| holdout.yaml | 12/12 | 0 | 16/16 | 0 | 0 | 4/4 |
| holdout2.yaml | 12/12 | 0 | 16/16 | 0 | 0 | 4/4 |

These sets still pass, so they cannot see the regressions above.

## 5. Gate

- **Protected paths:** `git diff cf98d6e 931552f` on eval_cases/, eval_results/, app/content.py, deploy/ and LICENSE is empty. protocol.py is not protected.
- **Tests:** no removed lines under tests/ (601efd3..931552f). No skip or xfail was added.
- **Corpus:** 447 → 548 messages. No message was removed or relabelled; the 101 added are verifier-3's held-out set.
- **Soft bound:** the false-alarm bound in test_adversarial.py grows mechanically with the number of controls (now 19 allowed). The formula itself is unchanged.
- **Gate status:** passes, but process issues remain:
  - One commit bundles the parser, protocol, main.py, impact.html, docs and two audit files.
  - The round-3 63-message grid was not added to the tests.

## Required before approval

1. Set `other_animal` (or at least `explicit_other` and R1) only when the animal is the stated biter: call `_explicit_animal_biter`. Treat swelling or pain after a lookalike bite at night as a possible snakebite. Extend ANIMAL_NOT_RE to all "rat" = "raat" forms ("kal rat", "aaj rat", "rat main/mai/ki/se/<digit>").
2. Put SELF_BITE under `can_suppress()`. Drop "bit into" and "teething" as suppressors, and remove `not SELF_BITE.search(text)` from the safety net.
3. Gate `snake_mention_only` on the absence of any person pronoun and of any contact verb. Or limit it to the explicit non-medical list (plant, game, film, pose and similar) and drop "what", "how", "kya", "kaise" and "keep" from INFO_WORDS.
4. Restore "body part + symptom" as a raise, or show with a held-out set that dropping it causes no false safes.
5. Make danger-sign matching robust to suffixes and SMS spellings: drop the end boundary for Latin stems, and allow inflections and both word orders in Devanagari. Add the missing verbs (threw up, talk, convulsing, panting, confused).
6. Add this set and the grids to the tests only after the fix. Then measure on a new held-out set.
