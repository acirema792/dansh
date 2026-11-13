# Checker verdicts, round 2 (R1b/R2 fixes)

Scope: d185b66, 88b9445, 0a69d76. HEAD during the run was 0a69d76; dbf7813, a loop-state commit, landed afterwards and was not reviewed. No files in /home/claude/dansh were edited. Scratch is /tmp/chk3:
- `head/` is a HEAD snapshot and `pre/` is a snapshot of 080eeae.
- Scripts: `harness.py`, `recheck.py`, `fresh3.py`, `diff.py`, `hb.py`, `hbgrid.py`, `edge.py`, `thorn.py`, `rotate.py`, `pw.py`.
- Outputs: `*_out.txt`, `recheck_*.txt`, `rot_*.txt`.

## Verdicts

- **d185b66 fix(R1b,R2-1..R2-4,R2-10): REJECT. It introduces new FALSE SAFES and breaks the safety invariant.**
  - The new `HUMAN_BITER` regex (parser.py) treats "my son **was bit**", "my daughter **got bit**" and similar as a human biting someone. It clears both `bite` and `unknown_bite`. The `MARKS` signal is wiped too.
  - On a 315-message grid of `<person> was/got bit [symptom]`, **252 lost the hospital referral**. At 080eeae, 0 did.
  - The `INJURY` rule, `sewing` in THORN and "keep snakes away" in PREVENT each add more false safes.
  - It also regresses 8 clear dog, monkey or scorpion bites that were verified fixed in r1b. They are now POSSIBLE snake plans, which say "Do NOT … wash the bite", and they lose the rabies/108 note.
  - It does fix most round-2 inputs: on the re-check set, not-OK fell from 138 to 22 out of 327.
  - Human review of the medical routing is recommended.
- **88b9445 fix(R2-5,R2-7,R2-8): REJECT. The 150 policy needs human sign-off (ESCALATE_HUMAN on that point).**
  - The Wilson CI is correct, and test mode now persists within a tab.
  - But the per-browser ID is self-reported and can be rotated freely. One IP can now produce **up to 150 counted "people" a day, up from 5**. I demonstrated 12 counted, all 0%→100%, from one IP in about 52 s.
  - None of this is disclosed. /impact (impact.html:46) and README:70 still say a device counts only 5 a day. impact.html:37 still claims the developers' runs are excluded.
- **0a69d76 docs(R2-9): REJECT.**
  - The source links are real and mostly support the claims.
  - The new sentence in BENCHMARK-RESULTS.md:31 is false: "about 180 audit messages … Every one is now a permanent test". 151 of the 244 audit and verifier inputs are not in tests/, and some still fail.
  - The IMPACT-SNAPSHOT.md link is still broken (README:6, EVIDENCE.md:8).
  - SUBMISSION.md:20 still says "under a second".
  - The ICMR "53% below poverty line" figure conflicts with press reports (47.5%), and the DOI could not be verified.

## 1. Tests and evals

- `python3 -m pytest -q tests`: **`214 passed in 4.42s`**
- Server: `DANSH_DB=/tmp/chk3/db/dansh.db uvicorn :8095`. `/api/health` returned `{"ok":true,"version":"1.0.0","commit":"0a69d76","llm":false,...}`. The server has been stopped.
- Eval results:
  - **cases.yaml:** "**18/18** bite cases sent to hospital (**0 false safe**)". `{cases 22, passed 22, false_safe 0, under_triage 0, over_triage 0, controls 4/4}`
  - **holdout.yaml:** "**12/12** … (**0 false safe**)". `{16/16, false_safe 0, controls 4/4}`
  - **holdout2.yaml:** "**12/12** … (**0 false safe**)". `{16/16, false_safe 0, controls 4/4}`
- The eval sets do not discriminate. They pass 100% while 252 of 315 "was/got bit" grid messages lose the hospital referral.

## 2. Re-run of every input listed as broken

The set is 327 unique inputs:
- verify-r1b.md (items 1-28, drooling, H2 borderline, pre-existing, over-triage);
- round-2 classes 1-8 and the false-alarm list;
- /tmp/aud2/probe/{fresh,r1}.json;
- /tmp/chk2 probe lists.

Not OK: **22 at HEAD, 138 at 080eeae.**

**Still FALSE SAFE (from the listed inputs):**
- `I felt a sharp pain on my foot in the paddy field and now it's swelling and burning`: OFF_TOPIC (aud2 fresh)
- `kaanta tha ya kuch aur, pata nahi, pair suj raha hai`: OFF_TOPIC (chk2 extra)
- `sui jaisi chubhan hui pair me raat ko`: OFF_TOPIC (chk2 extra)

**Still UNDER-TRIAGED (URGENT):**
- `snake bit my son, his eyes are not opening`
- `snake bit him, his lips are turning blue`

The vocabulary added only the exact test phrasings.

**REGRESSED in d185b66.** These were OTHER at 080eeae, and r1b verified them as fixed. Each now gets a POSSIBLE snake plan with "Do NOT … wash the bite" and no rabies note:
- `kutte ne kaata, shayad pagal tha`
- `a stray dog bit my daughter, maybe it was rabid`
- `my dog bit me, I think it needs a vaccine`
- `bandar ne kaata, shayad rabies ka khatra hai`
- `bichhu ne kaata, kuch upay batao`
- `scorpion stung me, i think it is serious`
- `bitten by a dog yesterday, I think it was rabid`
- `बंदर ने काटा, शायद`

Cause: `HEDGE_IGNORE_RE` only whitelists the phrasings the tests pin ("maybe rabies", "not sure if serious"). The removed `explicit_animal` guard no longer protects anything else.

**False alarms**
- New in d185b66:
  - `kaanta chubh gaya, khoon nikal raha hai`: CRITICAL
  - `saanp kyon kaatte hai`: URGENT
  - `I saw a snake in the garden, how to keep it away`: URGENT
- Still open:
  - `mosquito bites all over my arm`, `ant bit me` and `my tooth hurts when i bite`: POSSIBLE
  - `saanp ko ghar se door kaise rakhe` and `how to protect my family from snake attack this monsoon`: URGENT
  - `I am seeing two snakes in the yard, how to keep them out`: URGENT (down from CRITICAL)

**Fixed (all now pass):**
- round-2 classes 1, 2, 3 (in the tested phrasings), 4, 5 (the listed inputs), 6, 7 and 8;
- verify-r1b items 1-28;
- drooling;
- H2 "keep out";
- `rat bite i guess…`;
- `साँप का हमला, बचाव करो`;
- `two puncture wounds…`;
- `stepped on something … glass`;
- `cat scratched me, maybe infection` and `I pricked my finger while sewing`.

## 3. False-safe hunt

I wrote 100 new messages (60 bite, 20 danger-sign, 20 control) in `fresh3.py`. Each was checked with grep and appears in no test, eval file or earlier probe. I also ran targeted probes (`hb.py`, `hbgrid.py`, `edge.py`, `thorn.py`) and a 30,000-message differential fuzz against 080eeae (`diff.py`). In that fuzz, 583 messages lost the hospital referral. Most are word salad, but it surfaced the HUMAN_BITER class.

**A. NEW FALSE SAFES introduced by d185b66.** Each went to hospital at 080eeae and gets OFF_TOPIC or INFO at HEAD.

Caused by HUMAN_BITER:
1. `my son was bit on the foot and it's swelling`: OFF_TOPIC
2. `my son got bit, two marks on his foot`: OFF_TOPIC
3. `my daughter was bit on her toe, she is crying`: OFF_TOPIC
4. `my son got bit on the ankle, now he is vomiting`: OFF_TOPIC (with the vomiting flag)
5. `my brother got bit on his hand, it hurts a lot`: OFF_TOPIC
6. `my child was bit, there is a little blood`: OFF_TOPIC (with the bleeding flag)
7. `my baby got bit while sleeping, now very drowsy`: OFF_TOPIC (with the unconscious flag)
8. `son was bit, what do we do`: OFF_TOPIC
9. `daughter just bit on the leg pls help`: OFF_TOPIC
10. Grid: 252/315 of `{my son|my daughter|my baby|my child|my brother|my sister|my kid|son|daughter} {was bit|got bit|just got bit|bit on the foot|was bit on the hand}{"", swelling, two marks, vomiting, drowsy, what to do, help}`

Caused by the INJURY rule, which clears two-marks even with symptoms:

11. `he slipped in the courtyard, two marks on his ankle and it is swelling`: OFF_TOPIC
12. `my son fell off the cot, now two marks on his foot and he is vomiting`: OFF_TOPIC
13. `dadi gir gayi aangan me, pair pe do nishaan aur sujan`: OFF_TOPIC

Caused by "stitching" in THORN (plain_thorn ignores red flags):

14. `felt a prick while stitching, now feeling very drowsy`: OFF_TOPIC

Caused by "keep snakes away" being added to PREVENT:

15. `we think a snake got papa in the field, how to keep snakes away`: INFO

Borderline (the human biter is named, but the marks contradict it):

16. `my toddler bit my son?? but the marks are far apart and his foot is swelling`: OFF_TOPIC

**B. Pre-existing false safes still open.** These failed at 080eeae too. 14 of the 60 fresh bite messages failed:

17. `dunno what it was, it was thin and moved fast, then my leg started burning`: OFF_TOPIC
18. `पता नहीं क्या था, लंबा सा था, बच्चे के पैर पर निशान हैं`: OFF_TOPIC
19. `we assumed it was a dog but nobody saw it, he was bitten in the sugarcane field`: OTHER
20. `rat ne kaata hoga, par ab uski aawaz ladkhada rahi hai`: OTHER (slurred speech, rat)
21. `felt something sharp like two needles on my heel in the rice field`: OFF_TOPIC
22. `it felt like a thorn when I put my hand in the woodpile but now the hand is swelling up`: OFF_TOPIC
23. `thought it was a thorn while plucking tea leaves, now two red spots and pain going up`: OFF_TOPIC
24. `jaise sui chubi ho, dhaan ke khet me, ab dard upar chadh raha`: OFF_TOPIC
25. `his toe was in the water channel and something grabbed it, small puncture, now it throbs`: OFF_TOPIC
26. `after cleaning the cattle shed my hand has two bleeding points`: OFF_TOPIC (with the bleeding flag)
27. `baccha khet se aaya, ro raha hai, pair pe do lal daag`: OFF_TOPIC
28. `रात को खेत में पानी लगाते समय पैर पर कुछ लगा, अब झनझनाहट है`: OFF_TOPIC
29. `pambu kadichiruchu` (Tamil): OFF_TOPIC. Out of the stated en/hi scope.
30. `hav kadise` (Kannada): OFF_TOPIC. Out of the stated en/hi scope.

Thorn plus a danger sign, where R2-4 is only partly fixed because the override ignores red flags:

31. `kaanta chubh gaya, ab ulti aur chakkar aa raha`: OFF_TOPIC
32. `thought it was a thorn, now he is very drowsy`: OFF_TOPIC
33. `a thorn got me, now vomiting and can't breathe well`: OFF_TOPIC
34. `needle prick on my toe last night, now I'm sleepy and my urine is red`: OFF_TOPIC
35. `stepped on a nail I think, now my gums are bleeding`: OFF_TOPIC

Fixed since 080eeae (from the fresh set):
- `sap ne dash diya`
- `🐍 my dad`, `🐍🦶😭` and `🐍➡️👦 help`
- `सांप से बचाव कैसे करें, भाई के हाथ में सूजन है…`
- `pair me jaise kaanta chubha ho waisa laga…`
- `while sleeping on the floor my daughter woke up screaming…sleepy`

**C. Danger signs under-triaged** (URGENT, not CRITICAL, but still sent to hospital). 11 of 20:
- `snake bit my brother and his eyes are half closed, he looks drunk`
- `after the snakebite she keeps spitting, cannot get saliva down`
- `snake bit him and his breaths are very far apart`
- `साँप ने काटा, उसका शरीर ढीला पड़ गया है`
- `snake bite and his pee is like cola`
- `snake bit my son, he is having a fit`
- `snake bite, she is turning blue`
- `snake bit my dad and his neck is floppy`
- `snake bit him, he can't lift his head`
- `snake bit him, his tongue feels thick and words are coming out wrong`
- `snake bite, he says he cannot see properly, double`

Also, from the round-2 lists: `snake bit my son, his eyes are not opening` and `snake bit him, his lips are turning blue`.

## 4. False-alarm check (20 controls)

4 of 20 got a bite plan:
- `my 2 year old bites other kids at daycare`: POSSIBLE
- `how many people die of snakebite in india`: URGENT
- `मेरे बच्चे ने मेरी उंगली काट ली`: POSSIBLE
- `mosquito bite swelling on baby`: POSSIBLE

The other 16 are correct, including dog bites as OTHER, rose thorn, splinter, glass, first-aid kit questions and fever.

## 5. Integrity (88b9445)

- **Per-browser client ID.** The client ID is taken from the request body (`client`, 16-64 chars of `[A-Za-z0-9_-]`). It is never verified and can be rotated freely.
  - `/tmp/chk3/rotate.py` ran on the default config (device cap 5, network cap 150, real 20 s/30 s timings) from one IP with 12 random client IDs. It got **12/12 counted**, `unique_devices: 12`, dangerous choices 100%→0%, CI [75.7–100]→[0–24.3].
  - With `DANSH_MAX_PER_NETWORK=10` and 15 IDs, 10 were counted and 5 excluded. So rotation is **bounded only by the network cap: 150 a day per IP, 30x the previous 5.**
  - The network cap also counts already-excluded (too_fast) rows. Network-cap exclusions are labelled `device_cap`, so the two cannot be told apart on /impact.
  - The global rate limit was raised from 40 to 120 per minute per IP.
- **Disclosure: NOT disclosed.**
  - impact.html:46 is unchanged: "A device that completes more than 5 checks in a day only counts for its first 5". This is now inaccurate.
  - README:70 has the same wording.
  - There is no mention of the per-browser ID, the 150 network cap, or that a script can rotate IDs.
  - impact.html:37 still says "Test runs (including the developers'…) are excluded".
- **Test mode persistence (static/app.js).** It now uses **sessionStorage**, not the localStorage that R2-5 asked for. In a Playwright check:
  - `/?test=1` → Impact → /check kept `dansh_test=1`, showed the banner, and `/api/learn/start` carried `x-dansh-test: 1`.
  - A new tab, or a return visit after closing the tab, opened at `/check` loses test mode and is counted.
  - README:3 "Live" link still has no `?test=1`.
  - Verdict: partial.
- **Wilson CI.** `_wilson` matches the Wilson score interval. I checked 10 (k, n) pairs against an independent implementation; they differ by at most 0.1 (z=1.96 vs 1.95996). n=0 returns None. Caveat: the intervals are per marginal proportion. They are not a paired test (McNemar) of the before/after change.
- **Breakdowns.** Per-src and per-order n and percentages are present. No paired test.

## 6. Gate

- **Protected paths:** none touched. The files changed are:
  - d185b66: app/parser.py, app/protocol.py, tests/test_audit_r1.py, tests/test_audit_r2.py, tests/test_verify_r1b.py
  - 88b9445: app/main.py, app/store.py, static/app.js, static/impact.js, tests/test_integrity.py
  - 0a69d76: BENCHMARK-RESULTS.md, EVIDENCE.md, README.md, SUBMISSION.md
- **Assertions:** 0 `assert` lines removed, 16 added. No skip or xfail.
- **Fuzz list:** confirmed restored. `git diff 6c107f1 d185b66 -- tests/test_audit_r1.py` is empty. The bite list is again `["bit","bitten","kaata","काटा","attacked","hamla","fang marks","dasa"]`, and it passes.
- **Process:** d185b66 bundles about 9 findings (R1b, R2-1/2/3/4/10/13/14/16), which breaks "one finding per change". The new tests pin only the exact audit phrasings, so they do not catch the HUMAN_BITER, INJURY or animal-hedge regressions.

## 7. Docs: README "Why this problem"

- **Suraweera, eLife 2020** (link real; full text blocked, checked through the eLife press release, the ORA abstract and Yale E360). Supported:
  - 1.2 M deaths, average 58,000 a year;
  - about half of world deaths;
  - 1 in 250 before age 70;
  - 70% in 8 states holding about 55% of the population;
  - 94% rural;
  - more than 77% outside health facilities.
- **MoHFW NAP-SE** (medicaldialogues.in, a news report rather than MoHFW itself). Supported:
  - 3-4 M bites a year;
  - halve deaths by 2030;
  - "public education" and "referral" are named strategies.

  The same article also cites the CBHI figure of about 3 lakh cases a year, which the README omits.
- **ICMR, Nature Communications** (doi.org/10.1038/s41467-025-64849-2):
  - **The DOI could not be verified.** doi.org is not reachable from here, and an exact-string search returned nothing.
  - Press reports support 60 M people, 25 districts, 11 states, 0.33/100k, 43% outside hospital, ₹6,500 average, and ₹27,400 private vs ₹3,900 public. UP and Bihar are excluded.
  - **The "53% below poverty line" figure is disputed:** News Arena says 47.5%; OC Academy says 53%.
  - The "10 Nov 2025" date is unverified; press says only "this month", November 2025.
- **Wagle et al.** (researcher.manipal.edu): supported. 273 patients; tourniquet was the most-used first response (70%); VENOMS registry; "rapid transfer … associated with better outcomes". The README does not give the journal or year (PLoS NTD 2025).
- **Ralph et al., TRSTMH 2025** (doi 10.1093/trstmh/trae083, confirmed through infontd.org). Supported:
  - Timiri 69% and Jawadhu Hills 90% tourniquet use;
  - a healer was the first contact for 64% in Jawadhu Hills;
  - those healers did not refer to hospitals.

  The removed "healer use linked to higher mortality" was indeed unsupported, so removing it was correct.
- **Other doc problems still open:**
  - IMPACT-SNAPSHOT.md does not exist, yet README:6 and EVIDENCE.md:8 link it.
  - SUBMISSION.md:20 says "replies in under a second".
  - BENCHMARK-RESULTS.md:31 "Every one is now a permanent test" is false: 151 of 244 audit inputs are not in tests/.
  - impact.html:37 and :46 and README:70 still describe the old cap and the developer exclusion.
- **Done correctly:** the benchmark times now match `ran_at`, and the holdout2 header error is disclosed. The AF box is unticked. EVIDENCE.md and SUBMISSION.md now say "tourniquets in 69-90% in field studies".
