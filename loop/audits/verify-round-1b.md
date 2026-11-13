# Checker verdicts, round 1b (reworked fixes)

Scope: 6b2e024 fix(V1-V4), 915ef94 fix(V5-V7), 26d560c fix(H2). HEAD = 080eeae (the commit after H2 is docs only). No files in /home/claude/dansh were edited. Scratch is /tmp/chk2: pre-fix snapshot 01a6f42 in `pre/`, pre-H2 snapshot 458180e in `preh2/`, HEAD in `head/`, plus probe scripts and their outputs.

## Verdicts

- **6b2e024 fix(V1-V4): REJECT.** It introduces 21 new FALSE SAFES, each a POSSIBLE plan at 01a6f42 that is now OTHER or OFF_TOPIC with no go_hospital. That breaks the safety invariant in loop-constraints.md. It also re-opens 7 snake-attack false safes in the F2 class, and a fuzz test was narrowed so it no longer catches them. Human review is recommended, because this is medical routing.
- **915ef94 fix(V5-V7): APPROVE.**
  - /api/consult never returns 429 (60 of 60 got 200).
  - /api/learn/* still returns 429.
  - Chunked POSTs get 411 for every casing and TE-list variant I tried.
  - The LLM deadline is enforced and tested.
  - impact.js now has 10 `<div` and 10 `</div>`.
  - Process note: one commit bundles V5, V6, V7 and the markup fix, which breaks "one finding per change".
- **26d560c fix(H2): REJECT (low risk).** The "sees double" part is correct. But bare "keep out" in PREVENT downgrades a snake-near-a-person message from URGENT to INFO, against the maker's own rule (`test_snake_seen_with_person_still_urgent`). And "seeing two" raises a false CRITICAL on "seeing two snakes in the yard".

## 1. Tests and evals (run by me at HEAD 080eeae)

- `python3 -m pytest -q tests`: **`116 passed in 21.17s`**
- Server: `DANSH_DB=/tmp/chk2/db.sqlite uvicorn app.main:app --port 8097`. `/api/health` returned `{"ok":true,...,"llm":false}`. The server has been stopped.
- `run_eval.py` results. Summary lines are from latest.md, the JSON from latest.json:
  - **cases.yaml:** "**18/18** bite cases sent to hospital (**0 false safe**)". `{"cases": 22, "passed": 22, "false_safe": 0, "under_triage": 0, "over_triage": 0, "controls_correct": 4, "controls": 4}`
  - **holdout.yaml:** "**12/12** bite cases sent to hospital (**0 false safe**)". `{"cases": 16, "passed": 16, "false_safe": 0, "under_triage": 0, "over_triage": 0, "controls_correct": 4, "controls": 4}`
  - **holdout2.yaml:** "**12/12** bite cases sent to hospital (**0 false safe**)". `{"cases": 16, "passed": 16, "false_safe": 0, ..., "controls_correct": 4, "controls": 4}`
- **Caveats:**
  - All three sets are 100%, yet the regressions below go through. The eval sets cannot tell these regressions apart.
  - holdout2 is no longer held out: H2 was fixed against its first run (the maker says so).
  - BENCHMARK-RESULTS.md gives run times of 16:15 and 16:25 UTC, but the recorded run in live-holdout2-run1.md is 16:08:22, the same as the commit. That is a docs inaccuracy.

## 2. Re-run of every input verify-round-1.md listed as still broken

Results compare 01a6f42 with HEAD. All of these are now fixed:
- **Animal bites with doubt words** now give OTHER with other_bite, where 01a6f42 gave POSSIBLE:
  - `kutte ne kaata, kuch karo`
  - `my dog bit me, I think it needs a vaccine`
  - `a dog bit my son, maybe rabies? what to do`
  - `bandar ne kaata, shayad rabies ka khatra hai`
  - `monkey bit me, not sure what to do`
  - `bichhu ne kaata, kuch upay batao`
  - `scorpion stung me, i think it is serious`
  - `a bee stung me, maybe allergic`
- **False alarms** now give INFO or OFF_TOPIC:
  - `how to protect from snake attack in the fields`
  - `why do snakes strike, how to avoid them`
  - `my father has fever and vomiting, he slept badly`
  - `my baby is drooling a lot, teething`
  - `kaanta chubh gaya pair me`
- **Uncertain-bite inputs that used to give INFO** now give POSSIBLE with go_hospital:
  - `pair me kuch chubh gaya, kaise bachav kare`
  - `बेटे को कुछ चुभ गया खेत में, बचाव कैसे करें`
  - `two marks on his leg, how to protect him from infection`
  - `my son has two holes on his foot, how to protect him`
- **`a rat bit my son while sleeping on the floor, now he can't open his eyes`** now gives CRITICAL (rule R1d).
- **Danger signs are now kept**, and each input gives CRITICAL:
  - `saanp ne kaata, khoon nahi jam raha`
  - `khoon nahi rok pa rahe`
  - `khoon nahi thahar raha`
  - `ulti nahi thahar rahi`
  - `snake bite no ambulance bleeding a lot`
  - `snake bite, breathing is ok for now but getting worse`
- **`breathing is fine earlier but now he is gasping`** keeps the breathing flag; it gives OFF_TOPIC with 112/108 because no snake is mentioned.
- **Controls are unchanged and correct.**

Two are still not fixed. Both are over-triage, not unsafe:
- `cat scratched me, maybe infection` gives POSSIBLE. That is the snake plan with "do not wash", and no rabies advice.
- `I pricked my finger while sewing` gives POSSIBLE.

## 3. New probes

I sent 92 fresh messages in English, Hindi (Devanagari) and Hinglish, plus 35 follow-ups, through parse() and decide(). The scripts are /tmp/chk2/fresh.py, extra.py, hamla.py and h2.py.

### NEW FALSE SAFES from 6b2e024

Each of these gave POSSIBLE with go_hospital at 01a6f42. Each now gets no hospital plan.

**(a) An animal next to a bite verb overrides the doubt word, giving OTHER.** The new line `if f.other_animal and explicit_animal: f.unknown_bite = False` also wipes the explicit UNKNOWN markers ("pata nahi kisne"). The biter regex crosses commas (`kaata, bichhu`). This is exactly the case verify-round-1 asked to keep ("maybe a rat"). The new test only covers the phrasing where the doubt word sits away from the verb ("bitten while cleaning the cowshed, maybe a rat"). Inputs:
1. `maybe a rat bit him in the field, it was dark`
2. `maybe a dog bit him`
3. `I think a dog bit me but it was dark and I didn't see`
4. `I think a rat bit my daughter in the field`
5. `shayad kutte ne kaata, andhere mein dikha nahi`
6. `rat ne kaata shayad, pakka nahi pata`
7. `rat or something bit my son at night`
8. `pata nahi kisne kaata, bichhu ya kuch aur`
9. `pata nahi kisne kaata, chuha ho sakta hai`
10. `शायद चूहे ने काटा, रात को`
11. `cat bit? not sure, it was dark, two small holes`
12. `kutte ne kaata ya kuch aur pata nahi, do daant ke nishaan`
13. `i think a scorpion stung me but i did not see it, it was dark`
14. `not sure if a dog bit him or something else`

**(b) A THORN-list word anywhere in the message clears unknown_bite, giving OFF_TOPIC.** This happens even when the message has "two marks" or "do nishaan", says "maybe a thorn", or uses "like a needle" (a classic description of a snakebite). Inputs:
15. `pair me sui jaisa kuch chubha khet me, ab jalan ho rahi hai`
16. `felt a needle-like prick on my foot while walking at night`
17. `nail jaisa kuch chubha, do nishaan hai`
18. `two holes on his foot, maybe a thorn`
19. `was it a thorn? two marks and the leg is swelling`
20. `something pricked my child in the field, maybe a thorn, now he is crying a lot`
21. `kuch chubha, kaanta ya kuch aur pata nahi, raat ko khet me`

**(c) A weak bite word plus a prevention word, with no person word, gives INFO.** These are the same F2 class that round 1 found. Each gave URGENT at 01a6f42 and gives INFO now:
22. `snake attack in the field just now, how to protect the leg`
23. `snake strike on the hand, how to protect it`
24. `krait attack at night, how to protect`
25. `snake attack! how to protect, help fast`
26. `cobra attack, help, protect`
27. `saanp ka hamla, help, bachav karo`
28. `saanp hamla, bachav, help`

**Under-triage regression from 6b2e024.** "drool" and "drooling" were removed from speech_swallow, so these two drop from CRITICAL to URGENT (they still go to hospital):
- `snake bit him, he is drooling`
- `snake bit him and now he is drooling and can't talk`

### Possible false safes from 26d560c (H2), borderline

These gave URGENT at 458180e and give INFO now. No bite is stated, but a person is next to the snake, which the maker's own test treats as URGENT:
- `a snake came near my father, he is shouting, keep out`
- `snake entered the house and my child is near it, how to keep out`

**New false alarm from H2.** `I am seeing two snakes in the yard, how to keep them out` gave INFO and now gives CRITICAL, because "seeing two" maps to ptosis.

### Pre-existing false safes (also wrong at 01a6f42, still open)

- `something long slid over my foot in the paddy field and now there are two red dots`: OFF_TOPIC
- `stepped on something in the grass at night, felt like glass, now swelling`: OFF_TOPIC
- `two puncture wounds on her ankle after walking in the field`: OFF_TOPIC
- `rat bite i guess, now his eyes are closing`: OTHER. It has the ptosis flag but no night or floor word.
- `साँप का हमला, बचाव करो`: INFO

### Pre-existing missed danger signs (still URGENT)

- `saanp ne kaata, aankhein nahi khul rahi`
- `saanp ne kaata, peshab laal ho gaya`

### Other over-triage, unchanged

- `mosquito bites all over my arm`: POSSIBLE
- `ant bit me`: POSSIBLE
- `my tooth hurts when i bite`: POSSIBLE
- `how to keep snakes away from my house`, `saanp ko ghar se door kaise rakhe`, `how to protect my family from snake attack this monsoon`: URGENT

### What held up

Every fresh Hindi and English negation or stop-verb danger sign I tried gives CRITICAL. That includes "khoon ruk hi nahi raha", "खून नहीं रुक रहा", "सांस नहीं ले पा रहा", "hosh nahi hai", "bleeding won't stop", "no one can stop the bleeding" and "saans theek se nahi aa rahi". Clearly named animal bites stay OTHER. Uncertain bites with no animal named enter the protocol.

## 4. Gate and cheating check

- **Protected paths.** The three commits touch only these files, none of them protected:
  - app/parser.py
  - app/protocol.py
  - app/llm.py
  - app/main.py
  - static/impact.js
  - tests/test_audit_r1.py
  - tests/test_verify_r1.py
  - tests/test_integrity.py
- **Eval files.** eval_cases/holdout2.yaml was added in d506fdc (16:07:42) and has not changed since. Its first run was recorded in 458180e (16:08:22), and the H2 fix came after (16:08:55). The order is clean.
- **Deploy.** 01a6f42 (outside this scope) edits the protected deploy/cloud-config.yaml. It is declared in STATE Escalations item 4 and still needs human sign-off.
- **Test markers and assertions.** No skip or xfail markers were added, and no `assert` line was removed.
- **Declared test change 1** (tests/test_audit_r1.py fuzz, `attacked` to `attacked my`, `hamla` to `hamla kiya`): **this HIDES A DEFECT.**
  - With the original word list, the same seed (11) gives 56 of 2000 failures at HEAD, all `hamla` giving INFO.
  - Realistic messages in this class are real false safes (items 22-28 above).
  - The change is declared, but it loosens the test's coverage exactly where the regression is.
  - BENCHMARK-RESULTS.md still describes this fuzz as "2,000 snake + bite-word messages never produced...", which now overstates it.
- **Declared test change 2** (tests/test_integrity.py::test_f7_rate_limit retargeted to /api/learn/start): **LEGITIMATE.** The behaviour change is the declared V5 fix, and the new test `test_v_emergency_never_rate_limited` asserts both halves: consult always 200, and learn 429.

## 5. Emergency endpoint (live, :8097)

- 60 rapid `/api/consult` posts with "snake bit my father, he cannot breathe" gave 60 x 200. The over-limit reply is still the full CRITICAL plan.
- After that, 60 `/api/learn/start` posts gave 60 x 429, and `/api/learn/pre` gave 429. The consults use up the same per-IP bucket.
  - Note: on Indian carrier CGNAT, emergency traffic from other users behind the same IP will lock out the 3-minute check. This is minor.
- Chunked POSTs with a 60 KB body to /api/consult, /api/learn/start and /api/learn/pre each got **411** `{"error":"content-length required"}`.
- Raw-socket chunked requests with `Transfer-Encoding: Chunked`, `gzip, chunked` and ` chunked ` (padded with spaces) each got `HTTP/1.1 411 Length Required`.

## Required before re-approval of 6b2e024

- Treat the animal as the biter only when no doubt word qualifies it, and never clear an explicit UNKNOWN marker.
- Do not let a THORN word override "two marks", "do nishaan", "maybe a thorn" or "jaisa" / "like a" comparisons.
- Keep "attack/strike/hamla + protect/help" in the protocol unless the message is clearly generic, for example has no "just now", "help", "on the hand" or "leg".
- Restore drooling as a danger sign when a snake or bite is present.
- Put back the original fuzz word list, and add every input above as a test.
