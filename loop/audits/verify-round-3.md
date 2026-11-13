# Checker verdict, round 3: d500cbf "fix(V3)"

**Verdict: REJECT.**

- **Scope:** d500cbf. HEAD is 601efd3, which changes only one Hindi line in static/impact.html. parser.py and protocol.py are identical at both.
- **No edits** were made in /home/claude/dansh. Scratch is /tmp/chk4:
  - Data: `heldout.json` (101 labelled messages) and `grid.json` (63).
  - Scripts: `make_heldout.py`, `run_heldout.py`, `run_parent.py`.
  - Outputs: `heldout_out.txt` (HEAD), `heldout_parent.txt` (dbf7813), `grid_fs.txt`.
  - Clean clone: `clone/`.

## Why REJECT

1. **d500cbf adds new false safes.** On my held-out set it creates 7 new ones and fixes 2: 25 at d500cbf, 20 at its parent dbf7813. On a 63-message grid built around the three causes, 49 of 63 are FALSE_SAFE at d500cbf and 0 of 63 at dbf7813. These messages state a bite outright ("bitten", "kaata", "काटा"), so the labels are not debatable.
2. **The 447-message corpus is not in the commit.** `tests/data/` is git-ignored (`.gitignore:1: data/`), so `tests/data/adversarial.json` was never committed.
   - On a clean clone of d500cbf, pytest stops at collection with `FileNotFoundError: .../tests/data/adversarial.json` and runs **0 tests**.
   - So the headline "447-message auditor corpus as a test" is not true of the commit.
   - BENCHMARK-RESULTS.md cites a file that is not in the repo.
3. **The held-out false-safe rate is still high:** 25 of 73 bite or danger-sign messages get no hospital plan, and 15 of 27 danger-sign messages are under-triaged. The maker reports 0/0 on the corpus it tuned against; that does not carry over to new messages.

## 1. Tests and evals

- `cd /home/claude/dansh && python3 -m pytest -q tests -s | tail -5`:
  ```
  adversarial corpus: 447 messages; false alarms 1/62; animal misroutes 1/22
  .......................................................................................................................................................................................................................
  218 passed in 6.59s
  ```
  This passes only because the untracked file exists on this machine.
- Clean clone at d500cbf (and at 601efd3):
  ```
  ERROR tests/test_adversarial.py - FileNotFoundError ... Interrupted: 1 error during collection
  ```
- Server: `DANSH_DB=/tmp/chk4/db/dansh.db uvicorn :8093`. `/api/health` returned commit 601efd3. The server was stopped afterwards.

| Eval set | Bite cases sent to hospital | False safe | Cases passed | Under-triage | Over-triage | Controls correct |
|---|---|---|---|---|---|---|
| cases.yaml | 18/18 | 0 | 22/22 | 0 | 0 | 4/4 |
| holdout.yaml | 12/12 | 0 | 16/16 | 0 | 0 | 4/4 |
| holdout2.yaml | 12/12 | 0 | 16/16 | 0 | 0 | 4/4 |

The eval sets still pass 100%, so they cannot detect the failures below.

## 2. Held-out false-safe hunt

- **Set:** 101 new messages in English, Devanagari Hindi and Hinglish. Labels were fixed in `make_heldout.py` before any run.
- **Novelty:** I checked them by exact match, case-insensitive, against every file in tests/, tests/data/adversarial.json and eval_cases/. "saap" matched as a substring and was replaced by "saamp pair". There are 0 overlaps.
- **Disclosure:** the set is white-box. I wrote many messages after reading parser.py, to target its gaps. The rates are adversarial, not representative.

**Labels:** bite 46, crit 27, ctl 15, animal 13.

| Outcome | d500cbf | dbf7813 (parent) |
|---|---|---|
| FALSE_SAFE (bite or crit, no hospital) | **25** (bite 23, crit 2) | 20 (bite 17, crit 3) |
| UNDER (crit, not CRITICAL) | **15** of 27 | 15 |
| FALSE_ALARM (ctl given a hospital plan) | 10 of 15 | 8 |
| ANIMAL_MISROUTE | 4 of 13 | 4 |
| Correct | bite 23/46, crit 10/27, ctl 5/15, animal 9/13 | |

### Every FALSE_SAFE, verbatim (level reached in brackets)

**New in d500cbf (these went to hospital at dbf7813):**
1. `my father was bitten on the foot while eating dinner outside` (OFF_TOPIC)
2. `my son was bitten while eating at the dhaba at night` (OFF_TOPIC)
3. `bitten near the toe nail, what should I do` (OFF_TOPIC)
4. `ungli ke nail ke paas kaata, kya karu` (OFF_TOPIC)
5. `bit on the foot, gave him a glass of milk, what to do now` (OFF_TOPIC)
6. `बच्चे ने बताया कि पैर में किसी चीज़ ने काटा` (OFF_TOPIC)
7. `बच्चे ने कहा उसे काटा, वो रो रहा है` (OFF_TOPIC)

**Already false safe at the parent, still open:**

8. `a long thin thing came out of the rat hole and touched my hand, now it burns` (OTHER, rat)
9. `felt a pinch on my toe while drawing water from the handpump` (OFF_TOPIC)
10. `kuch kat gaya pair me` (OFF_TOPIC)
11. `my wife was gathering cow dung cakes and something nipped her wrist` (OFF_TOPIC)
12. `papa ko bhoose ke dher me haath dalte waqt kuch laga, ab haath bhaari` (OFF_TOPIC)
13. `he says it felt like an injection on his calf when he walked through the paddy` (OFF_TOPIC)
14. `could be a lizard, small marks on my son's hand` (OFF_TOPIC)
15. `definitely a rat bite, he's very sleepy now, he was sleeping on the floor` (OTHER, with a 108 note)
16. `rat bit him at night, now stomach pain and vomiting` (OTHER, with a 108 note)
17. `he was sleeping on the floor without a mosquito net and woke with a painful swollen hand` (OTHER, mosquito)
18. `stepped on what I thought was a thorn near the canal, there are two tiny red points` (OFF_TOPIC)
19. `my 3 year old came in from the garden screaming and holding his foot` (OFF_TOPIC)
20. `beta khet se rote hue aaya, pair pakad ke` (OFF_TOPIC)
21. `बच्चा खेत से रोता हुआ आया, पैर पर निशान है` (OFF_TOPIC)
22. `snaek bitt` (OFF_TOPIC)
23. `bitn on leg` (OFF_TOPIC)
24. `rat ko pair me kaata, ab pet dard` (OTHER). "rat" is a common typo of "raat" (night) and is matched as the animal.
25. `snkebite hlp` (OFF_TOPIC)

Some labels are arguable: 9, 10 ("kat gaya" can mean "got cut"), 14, 19, 20 and 22-25 (typos). Even without all of them, at least 16 false safes remain, including all 7 regressions.

For 15 and 16, the OTHER plan does show 108 first, so the risk is reduced. Under the corpus's own definition it is still a false safe: no hospital plan for classic krait signs (night, floor, drowsiness or vomiting).

### Every UNDER, verbatim (level reached in brackets)

1. `my grandfather was bitten in the shed and now his voice has gone funny` (POSSIBLE)
2. `the toddler was bitten in the field and is shaking all over and frothing` (POSSIBLE)
3. `snake bit my uncle, his eyes keep shutting by themselves` (URGENT)
4. `cobra bit her, she's struggling to get air` (URGENT)
5. `snake bite, he's gone blue around the mouth` (URGENT)
6. `saap ne dasa, haath pair dheele pad gaye` (URGENT)
7. `saanp ne kaata, gardan sambhal nahi raha` (URGENT)
8. `saanp ne kaata, muh se jhaag aa raha` (URGENT)
9. `sanp ne kata, neend se jag nahi raha` (URGENT)
10. `सांप ने काटा, पेशाब काला हो गया` (URGENT)
11. `सांप ने काटा, वो जाग नहीं रहा` (URGENT)
12. `सांप ने काटा, गर्दन नहीं संभल रही` (URGENT)
13. `krait bit him, he is talking like he is drunk` (URGENT)
14. `snake bit my son and his head keeps falling forward` (URGENT)
15. `snake bit him, he has never vomited like this, 4 times now` (URGENT). `_negated` treats "never" before a presence-type sign as a denial.

All 15 were also UNDER at the parent. The danger-sign vocabulary still only covers the exact phrasings the auditors used: "looks drunk" was added, "talking like he is drunk" was not; "dheela" was added, "dheele" was not; "काला पेशाब" was added, "पेशाब काला" was not.

### Other outcomes

- **False alarms (10):**
  - `snake plant care tips please`
  - `I bit into a green chilli and my mouth burns`
  - `I want to learn about cobra species for my school project`
  - `cobra pose kaise kare`
  - `Russell Peters show tickets`
  - `snakes and ladders game rules`
  - `the snake boat race in Kerala is on which date`
  - `मेरे बेटे के दांत निकल रहे हैं, वो सब कुछ काटता है`
  - New in d500cbf:
    - `rose thorn pricked my thumb while gardening at home, tiny drop of blood` (CRITICAL)
    - `my knee hurts after running` (POSSIBLE). The safety net counts a body part plus "hurts" as a possible snakebite.
- **Animal misroutes (4):** `a horse bit my arm`, `a squirrel bit my finger`, `a spider bit me on the neck`, `kankhajura ne kaata`. Each gets a POSSIBLE snake plan.

### Regression grid (`grid.json`)

63 messages built from three patterns:
- `<bitten-phrase> while eating/chewing ...`
- `<bite> near the nail / while sewing / glass / needle / sui`
- `बच्चे/बच्ची/बेबी ने ... काटा`

Result: **49/63 FALSE_SAFE at d500cbf, 0/63 at dbf7813.**

Control check: removing only "while eating", or only "nail", gives `bite=True` again:
- `bitten near the toe, what should I do` → bite=True
- `my son was bitten at the dhaba at night` → bite=True

## 3. Code review: what can still drop a bite signal

The commit's claim that a signal "may only be removed by can_suppress()" is **false**.

**Rules that set bite or unknown_bite to False:**
- **`SELF_BITE`, parser.py:416-417, outside can_suppress.** It sets `f.bite = False` whenever the text contains `while (eating|chewing)`, `bite my food`, `when i bite` or `bit my tongue/lip/cheek`, unless a snake is named, a flag word is present or there is swelling.
  - It runs after `victim` has set `f.bite = True`, so it overrides "was/got bitten".
  - It ignores night, outdoor, doubt, urgency and body parts.
  - "while eating" describes when it happened, not who bit. This causes regressions 1-2 and the grid's "eating/chewing" rows.
- **THORN rule, parser.py:425-427.** It now relies only on `can_suppress()`. The old `plain_thorn` refused to suppress when the text had an explicit bite word ("bit", "bitten", "kaata", "काटा"); that check was dropped.
  - THORN includes "nail", "glass", "sui", "needle", "sewing" and "stitching", which often appear next to a real bite.
  - `can_suppress()` does not check BODY_PARTS.
  - This causes regressions 3-5.
- **HUMAN_BITER, parser.py:420-422.** The regex now includes `(?:बच्चे|बच्चा|बच्ची|बेबी)\s+ने`, which matches any Hindi sentence with a child as subject ("बच्चे ने बताया/कहा", "the child said").
  - `can_suppress(allow_marks=True)` does not catch Hindi crying ("रो रहा" is not in BODY_CHANGE) or body parts ("पैर").
  - This causes regressions 6-7.
- **Weak-only general question, parser.py:431-433.** Guarded by can_suppress, body parts and WEAK_PAST. I found no false safe here.
- **INJURY marks rule, parser.py:423-424.** Guarded by can_suppress(allow_marks).

**Rules that block the raise to "possible snakebite" (outside can_suppress):**
- **`human_bite`** (any HUMAN_BITER match with no doubt word) disables the whole safety net. The only exception is the human-bite-with-symptom line, so the Hindi "बच्चे ने" match removes the net as well.
- **`explicit_other`** (any OTHER word with no doubt word) also disables the safety net, and the protocol's R1 returns OTHER.
  - d500cbf added "ant", "mosquito" and "bedbug" to OTHER, so phrases like "mosquito net" now count as a named animal. "rat hole" and the "raat"→"rat" typo do the same.
  - R1d sends another-animal cases to a possible-krait plan only for ptosis or speech signs, or for breathing or weakness signs at night or on the floor. Drowsiness, unconsciousness and abdominal pain or vomiting are left out, though these are typical krait signs. This is pre-existing (FS 15, 16, 24).

**Text rewrites and negation:**
- `BIT_IDIOM` and `SUCKED_BLOOD` (parser.py:383-384) rewrite the text before parsing. Both are pre-existing.
- **Level demotion:** `_negated` treats `never` as a denial for presence-type signs, so "never vomited like this, 4 times" loses the vomiting flag and drops from CRITICAL to URGENT. This is pre-existing; protocol.py did not change.
- The LLM merge (llm.py:83) only adds facts, as documented.

## 4. Integrity disclosures

**Fixed:**
- impact.html now discloses the 5-per-browser and 150-per-network caps. It says the browser ID is client-side and that up to 150 scripted checks a day can come from one network.
- It shows the number of distinct networks and the largest share from any one network.
- The developer-exclusion claim is gone, in English and, since 601efd3, in Hindi.
- README:70 matches the code (main.py:27-30, 232-233).
- Test mode now uses localStorage (app.js, impact.js), as R2-5 asked.
- The eval runner sends `x-dansh-test: 1` (run_eval.py:29).

**Residual:**
- Network-cap exclusions are still recorded as `device_cap` (main.py:242), so /impact cannot tell the two caps apart.
- The disclosure says IDs can be rotated by someone "who clears it repeatedly". In fact a script needs no browser at all: it can POST any `client` value (main.py:165-166).
- `max_share_one_network_pct` counts only counted rows, which is reasonable. The network cap also counts rows already excluded as too fast (store.py:117-123), which is not disclosed. That is conservative, so minor.

**Docs:**
- IMPACT-SNAPSHOT.md now exists, which fixes the broken link. It has one row with 0 checks.
- The poverty figure is now "about half (47.5–53%)", which resolves the conflict.
- SUBMISSION "under a second (about 0.4 s)" is unverified, but plausible: local median 3-5 ms.
- **BENCHMARK-RESULTS.md:31-33:**
  - The counts are correct (bite 217, crit 142, ctl 62, animal 22, selfharm 2 plus any 2, which the doc calls "4 other"), and so is "445/447".
  - But it names `tests/data/adversarial.json` as the corpus, and that file is not in the repository.
  - It also says the held-out measure is "reported in loop/audits/". The round-2 verifier report, verify-r2, which recorded 46 failures among 100 fresh messages, is not in loop/audits/. The tracked files are round-1, round-2, verify-round-1 and verify-round-1b.
- README:6-7 still headlines "0 false 'safe'" from the 12-case held-out set. A fresh set gives 25 of 73 false safe.

## 5. Gate

- **Protected paths:** none touched. Changed files are docs, app/main.py, app/parser.py, static/*, and the new tests/test_adversarial.py. deploy/**, eval_cases/, app/content.py and app/protocol.py are unchanged.
- **Tests:** `git diff dbf7813 HEAD -- tests` has no removed lines. Nothing was skipped or marked xfail, and no assertion was loosened.
- **Problem:** the new test depends on an untracked, git-ignored file. On a clean checkout the whole suite fails at collection and runs 0 tests. That is worse than loosening one test. The fix is to force-add the file or rename the folder so it is not ignored, and to commit it.
- **Process:** one commit again bundles the parser rewrite, the corpus, the integrity work and the doc fixes.

## Required before approval

1. Commit `tests/data/adversarial.json` (it is ignored by `data/`) and show the suite passes on a clean clone.
2. Bring SELF_BITE under `can_suppress()`, and do not let it override `victim`. Restore the "explicit bite word blocks the thorn rule" check. Remove `बच्चे ने` from HUMAN_BITER, or require a human object. Add the regression grid and this held-out set to the tests.
3. Let OTHER suppress the safety net only when the animal is the stated biter, not when the word appears anywhere ("mosquito net", "rat hole", "rat" as a typo of "raat"). Add unconscious and vomiting to R1d at night or on the floor.
4. Broaden the danger-sign vocabulary by meaning, not by the exact audit phrasings. Stop treating "never" as a denial of a presence sign.
5. Human medical review of the R1 OTHER routing for nocturnal "rat" bites with drowsiness or vomiting.
