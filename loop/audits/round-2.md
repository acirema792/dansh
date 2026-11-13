# Dansh audit, round 2 (independent, read-only)

Date: 2026-11-13 16:10–16:40 UTC. HEAD 080eeae. Scratch is in /tmp/aud2: probe scripts in `probe/`, eval bundles in `cases/`, `holdout/` and `holdout2/`, screenshots in `shots/`, and the race test in `race.py`.

The live site and the STG PDF could not be reached from the shell (the proxy refused them). I read the STG through WebFetch. Everything else was run locally (`DANSH_DB=/tmp/aud2/db/dansh.db uvicorn :8096`, LLM off, the same configuration the live evals used).

## What I ran
- **pytest:** `python3 -m pytest -q -p no:cacheprovider tests` gave **116 passed** in 23.4 s.
- **Evals (local):**

  | Set | Exact | Bites sent to hospital | False safe | Controls |
  |---|---|---|---|---|
  | cases.yaml | 22/22 | 18/18 | 0 | 4/4 |
  | holdout.yaml | 16/16 | 12/12 | 0 | 4/4 |
  | holdout2.yaml | 16/16 | 12/12 | 0 | 4/4 |

  holdout2 scored 14/16 on its recorded first live run. Both misses are fixed by 26d560c.
- **Re-check of round 1 and the verifier:** 73 inputs from round-1 table B, the verifier's NEW-A/NEW-B lists and its residual lists, run through `parse()`/`decide()`.
- **Fresh probes:** 80 new messages (`/tmp/aud2/probe/fresh.json`).
- **API abuse:** chunked bodies, oversize bodies, the rate limit, src injection, a device-cap race with 10 parallel completions spaced at real timings, and path traversal.
- **Playwright** screenshots at 360x740 (hi-IN locale).
- **STG 2017** text checked through WebFetch.

---

## Round-1 and verifier findings: are they fixed?

| Item | Status |
|---|---|
| F1 dropped danger signs (12 table-B inputs) | **Fixed.** All CRITICAL with the flag kept. |
| Verifier residual drops (khoon nahi jam/rok/thahar, "no ambulance bleeding", "ok for now but getting worse") | **Fixed** (7/7). |
| F2/F3 false safes (12 inputs) | **Fixed.** All POSSIBLE/URGENT/CRITICAL. |
| Verifier R2 gap (chubh / two marks + bachav/protect) | **Fixed** (4/4). |
| Verifier NEW-A (named dog/monkey/scorpion/bee + hedge got the snake plan) | **Fixed** (8/9). `cat scratched me, maybe infection` still gets POSSIBLE with "don't wash" ("scratch" is not a biter verb). |
| Verifier NEW-B false alarms | **Fixed** (5/6). `I pricked my finger while sewing` gives POSSIBLE. |
| Round-1 "missed danger-sign vocabulary" (B section) | **NOT fixed: 14/16 still URGENT.** collapsed, passed out, convulsions, fits, jhatke, sleepy, neend aa rahi, gasping, haanf raha, chest tight, urine is red, peshab laal, aankhen jhuk rahi, palke bhaari. Only "unable to swallow" and "slurring" were added. |
| Round-1 Hinglish self-harm (`main marna chahta hoon`) | **NOT fixed.** |
| F4 XFF | Fixed in code. A forged XFF only works from a trusted proxy (127.0.0.1). The Caddy behaviour still has to be confirmed live. |
| F5 too-fast exclusion | Works. But see R2-6: a script that simply waits passes. |
| F6 whitelists + CSV guard | Works. |
| F7 body limit / chunked | Works: chunked gives 411, oversize gives 413. |
| V5 emergency never gets 429 | Works: 60/60 consults returned 200. Over the limit there is no LLM and no logging. |
| F11 updater gate / rollback / backup | **Not done** (deploy/** is protected). |
| F12 headers | Done: CSP, HSTS, XFO and HEAD / all present. |
| F13 impact.js markup | Fixed. The page renders with no console errors. |
| Escalation 2 (the LLM cannot re-add a denied flag) | Still open, and now matters more (see R2-2). |
| Escalation 1 (bee/scorpion content) | Still open. Scorpion danger signs get 108 first, and `other_bite` does mention scorpion → 108, but there is still no anaphylaxis line. |

---

## Scores

### A. Event fit: 6.5 / 10
**Strengths**
- README.md:24-36 is a clear, honest sizing table. It shows both the Million Death Study estimate (~58k/yr) and the far lower ICMR 2025 estimate side by side, and says they disagree (README.md:36, CLAIMS.md:18). That is unusually honest and defensible.
- The ICMR figures are consistent with press coverage: 0.3/100k, 11 states, about half of deaths before hospital, over half below the poverty line.
- The severity row covers out-of-pocket cost, private vs public, and the poverty share.
- CLAIMS.md tiers, including NOT-CLAIMED, are good practice.
- BENCHMARK-RESULTS.md lists the misses rather than hiding them.

**Problems**
- **Sources are not linked.** The README source column (README.md:28-34) gives names only, with no URLs. SUBMISSION.md:46 and EVIDENCE.md:6 both say "sources linked".
- **Severity lacks disability numbers.** There are no amputation, permanent-disability or lost-income figures. EVIDENCE.md:6 mentions "amputations from tourniquets" with no number.
- **README.md:6 and EVIDENCE.md:8 link IMPACT-SNAPSHOT.md, which does not exist.**
- **The benchmark timestamps are inconsistent and some are in the future.**
  - BENCHMARK-RESULTS.md:21-23 say the live runs were at "16:15" and "16:25".
  - eval_cases/holdout2.yaml:1 says it was "Written ~16:20 UTC".
  - The recorded `ran_at` values are 16:07:22 and 16:08:22, and holdout2 was committed at 16:07:42.
  - When I read these files the clock said 16:17.
  - A judge who checks will doubt the "written before the run" claim even though git order supports it.
- **SUBMISSION.md:65 pre-ticks "Built using AgentFoundry"** while AGENTFOUNDRY.md:18 says it has not been done yet. This is the eligibility gap.
- **README.md:70 and impact.html:37 say developer traffic is excluded.** In fact it is excluded only when `?test=1` is on the URL (R2-5).
- **SUBMISSION.md:20 says "replies in under a second".** That is true only with the LLM off; the LLM budget is 2.5 s.

### B. Medical safety: 6.5 / 10
**What is solid**
- The architecture: invariants on every response, a deterministic engine, every round-1 table input fixed, and 54/54 eval cases passing.
- Content checked against the STG 2017 text:
  - "Do not wash the wound" (p.9) matches.
  - Tourniquet/gangrene (p.9) matches.
  - ~70% non-venomous (p.7) matches.
  - Immobilise like a fracture, remove rings/shoes (p.8) matches.
  - Nil by mouth (p.8) matches.
  - Traditional remedies have no proven benefit (p.8) matches.
  - 24 h observation (p.10) matches.
  - Krait, early morning, no marks (p.17) matches.
  - The p.20 danger-sign list matches `critical_signs`.

**Content deltas (protected file)**
- `recovery_position` (content.py:82-87) says "on their side". STG p.8 says "prone, on the left side".
- `nil_by_mouth` (content.py:76-81) cites p.8, but the aspirin/NSAID warning is on p.45 and alcohol is not in the STG.
- There is no eye-irrigation item for a spitting cobra. The STG is silent on this too.

**Fresh probing found these failures** (each is POSSIBLE+ expected unless noted):

| # | Class | Example inputs | Got | Root cause |
|---|---|---|---|---|
| 1 | **Snake + symptom + prevention word gives INFO** | `a snake was near my son and now his leg is swollen, how do we protect him`; `snake in the house, my daughter is crying and her hand has two small wounds, how to keep snakes out`; `सांप घर में था, बेटे के पैर पर दो घाव हैं, बचाव कैसे करें`; `saanp ke paas khel raha tha beta, ab pair suj gaya, bachav kaise karein`; `saanp ghar me ghus gaya, beti ke pair me dard hai, bachav kaise kare`; `how to protect my son, a snake touched his foot` | INFO (prevention tips, 108 button only) | protocol.py:91-92: R2 ignores swelling, pain, wounds and person words when there is no literal bite word |
| 2 | **"no breathing" read as a denial** (STG p.20 lists respiratory arrest) | `snake bite no breathing`; `saanp ne kaata, no breathing, help`; `snake bit him, is his breathing ok? it sounds strange`; `how do I know if his breathing is ok` | URGENT; breathing put in `negated`, so the breathing follow-up question is removed (screenshot plan_nobreath.png) | parser.py:184 NEG_BEFORE `no` + flag; parser.py:186 NORMAL_AFTER fires inside a question |
| 3 | **Danger-sign vocabulary still missing** (STG p.20: unconsciousness, dark urine, respiratory distress) | collapsed, passed out, fits/convulsions/jhatke, gasping, haanf, lips turning blue, gala band, hosh me nahi, can't hold head up, gardan latak, no strength, eyes not opening, aankh nahi khul, peshab laal, urine is red | URGENT (no critical note, no recovery position) | parser.py:93-118 FLAG_WORDS |
| 4 | **Krait signs without a bite word give OFF_TOPIC** | `papa ki aankhen nahi khul rahi subah se`; `bacche ki palke gir rahi hai, raat ko zameen par soya tha` | OFF_TOPIC | Hinglish ptosis forms missing ("aankhen nahi khul", "palke"); R3b only fires on a recognised flag |
| 5 | **Thorn rule (V4) suppresses real bite descriptions** | `felt like a needle prick in the field at night, now swelling`; `pair me sui jaisa chubha khet me, ab sujan aur chakkar`; `kuch chubh gaya, keel jaisa laga, ab pair sooj raha aur ulti ho rahi` | OFF_TOPIC (the last one even has vomiting) | parser.py:248-295: THORN clears unknown_bite and bite whenever "needle/sui/keel/nail/glass" appears, even as a simile, with symptoms, or in a field at night |
| 6 | **Named non-snake animal + neuro signs, or a doubtful animal** | `a rat bit my son, now his eyelids are drooping`; `we think a rat bit grandpa, he is vomiting and cannot swallow`; `I thought it was a rat but it was long and black and it bit my son`; `was it a scorpion? my son was bitten in the field and is drowsy` | OTHER (108 first, but rabies "wash 15 min" text, no snake plan) | protocol.py:75 R1d needs night/floor; parser.py:85 HEDGE lacks "we think", "i thought", "was it"; parser.py:288 hedge is cancelled by an explicit biter |
| 7 | Self-harm in Hinglish | `main marna chahta hoon, saanp ne kaata`; `mujhe jeena nahi hai` | No crisis line | parser.py:90-91 has only the Devanagari forms |
| 8 | Unusual phrasings (S1) | `🐍🐍 help my son`; `साप चावला` | OFF_TOPIC | 🐍 is not a snake token; Marathi spelling |

- **False alarms** (not unsafe, but they cost credibility): `my baby bit my finger`, `I bit my tongue while eating`, `teeth marks from my toddler biting my arm`, `my son fell and has two marks on his knee from the stairs`, `what should I keep at home for snakebite first aid`, `is there a snake helpline in Bihar`.
- **LLM merge is not strictly monotone** (llm.py:88-91 with protocol.py:121-125,157). The model can set `self_harm=True`. That turns a bite into SUPPORT with calls `["14416","112","108"]`, so 108 drops to third. The LLM is off in production, so this risk is latent.
- **Bottom line.** All benchmark sets pass, but 80 fresh probes produced:
  - about 22 false safes or misroutes (classes 1, 4, 5, 6, 8);
  - 12 under-triages (classes 2, 3);
  - 2 missed self-harm messages.

  None of these yields "stay home". The INFO, OFF_TOPIC and OTHER plans all carry a 108 button. But classes 1, 2 and 5 are exactly the phrasings frightened relatives use. The eval sets are too small to catch these classes, which is the same lesson as round 1.

### C. Impact-measurement integrity: 6.0 / 10
**Strengths**
- The XFF spoof is closed.
- The too-fast filter works.
- The device-cap race is safe: 10 parallel completions from one IP were counted as exactly 5, with 5 excluded as `device_cap`.
- Whitelists, the CSV guard, excluded counts shown publicly, an honest limits paragraph (impact.html:47), and a raw CSV.

**Problems**
- **A scripted run that just waits passes every filter.** `/tmp/aud2/race.py` waited 21 s and 31 s and produced 5 counted "people" at 0% → 100% dangerous → 0%, from one IP in 52 s (screenshot shots/impact.png). N IPs give 5N perfect "improvements" a day. The quiz answers are public in app/quiz.py. This is acceptable only if the team discloses it and watches per-`src` numbers.
- **Test mode is not sticky** (app.js:6; links at app.js:262-263, index.html:20, impact.html:32).
  - It is only on while `?test=1` is in the current URL.
  - The "Back to emergency help" link, the /impact nav and the /impact → "3-min check" link all drop it.
  - The README's "Live" link (README.md:3) has no `?test=1`.
  - JUDGES.md:23 tells judges to "answer badly on purpose". A judge who arrives through the README, or who navigates away and back, will be counted as a large real "improvement". That contaminates rubric 4 in the team's favour.
- **Shared networks.** A classroom or an ASHA training on one Wi-Fi or NAT counts only 5 people a day (device_cap). It also hits 429 on `/api/learn/start` after 39 starts a minute (main.py:44,79). I measured 60 starts: 39 got 200 and 21 got 429. The obvious field campaign (one school class) would lose most of its data, and users would see an error.
- **The page cannot show counterbalancing working.** /impact and /api/impact give no breakdown by `src` or by form order. `by_form_order` is counts only, with no pre/post score per order. There are no confidence intervals and no paired test.
- **No real data yet.** IMPACT-SNAPSHOT.md is missing and there are no follow-up or retention measures. The live numbers are near zero. That is expected, but nothing in the repo yet shows a distribution plan that is being carried out.
- `started` (shown publicly) can still be inflated at 40 a minute per IP. This is minor.

### D. Security: 7.0 / 10
**Good**
- CSP with no inline script, HSTS, XFO DENY, nosniff and Permissions-Policy.
- Body limit plus chunked rejection.
- Per-IP token bucket.
- Pydantic validation (lang regex, `answered` coerced to bool).
- `src`, `state` and `role` whitelisted.
- `esc()` on all server strings.
- Path traversal on /static returns 404.
- Session ids from `secrets`.
- Salted daily device hash.
- The salt file is created with mode 0600.

**Problems**
- **Deploy privilege escalation (protected deploy/cloud-config.yaml:41-55).**
  - The repo is chowned to `dansh` (the app user, :54).
  - The root timer runs `git fetch/reset --hard` in it.
  - `git config --system --add safe.directory /srv/dansh/app` (:55) disables git's own guard against this.
  - So an app compromise can write `.git/config` (`core.fsmonitor=<cmd>`) and get root within 5 minutes.
  - The updater also runs `pip install` as root.
- Caddy runs as root (:75-86), and its binary is downloaded without a checksum (:69).
- `_buckets.clear()` at 50k keys (main.py:55) lets anyone with many IPs reset every limit.
- `/api/docs` is public. That is fine, but it is noted.

### E. Reliability and deploy: 6.0 / 10
**Good**
- The LLM has a hard 2.5 s wall-clock deadline (llm.py:43-50) with fallback to keywords.
- The emergency endpoint never returns 429.
- The client falls back to 108/112 on any error (app.js:168-169).
- Overpass has a 16 s abort and a map fallback.
- The Docker image has a healthcheck and runs as non-root.
- systemd uses Restart=always.

**Weak**
- **Self-updater** (cloud-config.yaml:41-52):
  - It deploys every push to main within 5 minutes, with no test or health gate and no rollback.
  - A bad commit in the next 24 h breaks the judged demo silently.
  - `set -e` plus Restart=always means a crash loop stays live.
- **No backup of the SQLite file**, which holds the only rubric-4 evidence, on a single VM.
- `ufw allow ...` is run but `ufw enable` never is (:87, :99-100), so the "firewall" is off. Uvicorn binds 127.0.0.1, so the exposure is small.
- If dansh-install fails before :88, the root `python3 -m http.server 80` boot-log server keeps port 80 and Caddy cannot bind.
- Dockerfile:14 `FORWARDED_ALLOW_IPS=127.0.0.1` puts every PaaS user behind one IP, if the Docker path is ever used (verifier note, unchanged).

### F. Testing: 7.0 / 10
**Good**
- 116 tests: every round-1 and verifier input is pinned (tests/test_audit_r1.py, tests/test_verify_r1.py).
- A 3,000-message fuzz plus a 2,000 snake+bite fuzz.
- Integrity tests, and the F4 mutation test is real.
- Three eval sets with frozen expectations, and an honest miss log.

**Gaps**
- No test covers any of the eight classes above. In particular there is none for "symptom + prevention word", "no breathing", the round-1 vocabulary list, or thorn-plus-symptom.
- The fuzz never mixes symptoms with prevention words.
- The LLM path has never been evaluated.
- There are no frontend tests, for example the test-mode persistence that R2-5 needs.
- The eval sets are still small and written by the builders. All three now pass 100%, so they no longer discriminate.

### G. Code quality and UX: 7.0 / 10
**Good**
- The code is small and readable, with a rule trace.
- No horizontal overflow at 360 px on / or /impact.
- No console errors.
- The Hindi plan renders well (shots/plan_nobreath.png).
- aria-controls is present.
- The language switch no longer re-logs the consult.

**Weak**
- On /impact at 360 px, the "Dangerous choice" column is clipped inside the scroll wrapper ("Dange choice").
- The /impact nav labels are English only.
- The plan language follows the UI language, not the message: an English message on a hi-IN phone gets a Hindi plan. The toggle fixes it, but this surprises English-speaking judges.
- Test mode is not sticky (R2-5).

**Weighted:** A 6.5×.30 + B 6.5×.25 + C 6.0×.15 + D 7.0×.10 + E 6.0×.10 + F 7.0×.05 + G 7.0×.05 = 1.95 + 1.625 + 0.90 + 0.70 + 0.60 + 0.35 + 0.35 = **6.475**

---

## What the team must do in the next ~24 h (rubric 4)
1. **Fix test mode first** (R2-5), so that judge and developer clicks cannot inflate the numbers. Then start distribution.
2. **Run 3-4 named `src` campaigns** (for example `?src=asha_<district>`, `?src=school_<name>`, `?src=farmer_wa`). Each person should use their own phone and mobile data rather than a shared Wi-Fi, until R2-6/7 is fixed.
3. **Add a per-`src` and per-form-order table to /impact** (R2-8).
4. **Commit a dated IMPACT-SNAPSHOT.md** containing `/api/impact` JSON plus the CSV. Commit one at mid-day and one before submission, and back up the DB off the box (R2-11).
5. **State n with a 95% CI and the excluded counts in the submission.** Do not round up, and keep the limits paragraph.

## What only the live site can show
- That Caddy (version installed from `api/download`) ignores a client-sent X-Forwarded-For, so the device cap holds for real. Check with `curl -H 'X-Forwarded-For: 1.2.3.4'` ×6 completions.
- That commit 26d560c (the holdout2 fixes) is actually deployed, and which commit is live. /api/health has no git SHA; adding one would help.
- Real latency and Overpass results from Indian mobile networks; geolocation over HTTPS.
- Whether real users on Jio/Airtel CGNAT or a shared Wi-Fi run into device_cap or 429 (`excluded.device_cap` growing on /impact).
- The real `/api/impact` numbers: n, the A→B vs B→A split, the shared count, the per-`src` split (CSV only).
- That the self-updater has not left a broken or crash-looping service, and that no stray install.log server is still on :80.
- The WhatsApp share preview (og tags), and Devanagari rendering on low-end Android.

OVERALL_SCORE=6.5

---

## Findings (top 10 first)

**R2-1 (S3): A snake mention plus a symptom plus a prevention word gives INFO (prevention tips).**
- **Inputs:** 6 inputs in table class 1, for example `a snake was near my son and now his leg is swollen, how do we protect him` and `सांप घर में था, बेटे के पैर पर दो घाव हैं, बचाव कैसे करें`.
- **Files:** app/protocol.py:91-92, app/parser.py:87-89. Not protected.
- **Fix:** In R2, also require `not (f.swelling or person-and-snake or any wound/pain word)`. The minimal form is `general and not (f.bite or f.unknown_bite or f.occult_krait or flags or f.swelling or (f.snake and person))`. Add `घाव|ghav|wound|wounds|dard|pain` to the bite-ish UNKNOWN list when a snake is present. Add these 6 inputs as tests.

**R2-2 (S3): "no breathing" is read as a denial of breathing difficulty. In an emergency it means respiratory arrest (STG p.20).**
- **Effect:** The case drops from CRITICAL to URGENT and the breathing follow-up question is suppressed. Questions such as "is his breathing ok?" are also read as denials.
- **Files:** app/parser.py:184-187. Not protected.
- **Fix:**
  - Do not let a bare `no`/`never` deny the inability-type flags (breathing, unconscious, ptosis, weakness). Require a qualifier (`no difficulty/problem/trouble ...`).
  - Skip NORMAL_AFTER when the clause ends in `?` or starts with `is|how|kya`.
  - Escalation 2 (letting the LLM re-add a denied flag) is the backstop; it needs a human ruling.

**R2-3 (S2): The round-1 danger-sign vocabulary is still missing (14 of 16 terms), plus new gaps.**
- **Terms:** collapsed, passed out, fits/convulsions/jhatke, gasping/haanf, lips blue, chest tight, gala band, hosh me nahi, can't hold head up, gardan latak, no strength, eyes not opening, aankh(en) nahi khul, palke, urine is red, peshab laal.
- **Files:** app/parser.py:93-118. Not protected.
- **Fix:** Add the words to FLAG_WORDS, mapping:
  - unconscious: collapsed, passed out, hosh me nahi, fits;
  - breathing: gasping, haanf, blue lips, gala band;
  - weakness / neck: head drop, gardan;
  - ptosis: aankh nahi khul, palke;
  - bleeding: urine red, peshab laal.

  Add a parametrised test.

**R2-4 (S2): The thorn rule (V4) turns real bite descriptions into OFF_TOPIC.**
- **Inputs:** `felt like a needle prick in the field at night, now swelling`; `pair me sui jaisa chubha khet me, ab sujan aur chakkar`; `kuch chubh gaya, keel jaisa laga ... ulti`.
- **Files:** app/parser.py:248-295. Not protected.
- **Fix:** Apply the thorn override only when there is no swelling, no red flag, no night/field context and no simile (`jaisa|like|jaise`). Otherwise keep `unknown_bite`.

**R2-5 (S2, impact integrity): Test mode is not sticky, so judge and developer clicks get counted. JUDGES.md tells judges to "answer badly on purpose".**
- **Files:** static/app.js:6,262-263; static/index.html:20; static/impact.html:32; README.md:3; static/impact.html:37 (claim). Not protected.
- **Fix:**
  - Persist `?test=1` in localStorage (`dansh_test=1`) and send the header whenever it is set.
  - Carry it on internal links.
  - Add `?test=1` to every judge-facing URL in the README.
  - Reword "including the developers'" to describe what is actually enforced.

**R2-6 (S2, impact integrity): A scripted run passes every filter (5 perfect improvements per IP per day; demonstrated).**
- **Files:** app/main.py:224-238, static/impact.html:46-47. Not protected.
- **Fix:**
  - Store a random client id (localStorage) next to the IP hash.
  - Exclude sessions with a perfect post score whose pre answers are all-wrong in a fixed pattern. Or simply publish the "0 → 100% on all six" count separately.
  - Disclose in the limits paragraph that the timing filter can be defeated.

**R2-7 (S2, impact): A shared Wi-Fi or NAT (a classroom or ASHA training) is capped at 5 counted people a day and gets 429 after about 39 starts a minute.**
- **Files:** app/main.py:27,44,79. Not protected.
- **Fix:**
  - Rate-limit `/api/learn/*` per session rather than per IP. For example, allow about 200/min per IP, and 1 start per 10 s per client id.
  - Key the device cap on the client id plus the IP hash.
  - Show `device_cap` exclusions per `src` so campaign losses are visible.

**R2-8 (S2, rubric 4): /impact cannot show that counterbalancing or campaigns work.**
- **Missing:** a per-`src` table, pre/post by form order, n with a 95% CI, and a paired sign test.
- **Files:** app/main.py:264-328, static/impact.js. Not protected.
- **Fix:** Add `by_src` and `by_form_order_scores` (mean pre/post per order), plus a Wilson CI on the dangerous-choice proportions.

**R2-9 (S2, eligibility/honesty): The submission and judge docs over-claim or have broken references.**
- SUBMISSION.md:65 pre-ticks AgentFoundry; AGENTFOUNDRY.md:18 says it is not done.
- README.md:6 and EVIDENCE.md:8 link IMPACT-SNAPSHOT.md, which does not exist.
- SUBMISSION.md:46 and EVIDENCE.md:6 say sources are linked; README.md:28-34 has no URLs.
- BENCHMARK-RESULTS.md:21-23 and eval_cases/holdout2.yaml:1 give times (16:15, 16:20, 16:25) that contradict the recorded `ran_at` (16:07-16:08) and the commit times. They were in the future when I read them.
- SUBMISSION.md:20 says "under a second".
- **Files:** docs (not protected); eval_cases/holdout2.yaml (PROTECTED: needs human sign-off; a comment-only correction).
- **Fix:**
  - Do the AF session and fill AGENTFOUNDRY.md.
  - Add the source URLs.
  - Create the snapshot.
  - Correct the times to the ran_at values.

**R2-10 (S2): Another animal named alongside neuro signs, or with doubt phrasing, gets the rabies text instead of the snake plan.**
- **Inputs:** `a rat bit my son, now his eyelids are drooping`; `we think a rat bit grandpa, he is vomiting and cannot swallow`; `I thought it was a rat but it was long and black...`; `was it a scorpion? my son was bitten ... drowsy`.
- **Files:** app/protocol.py:75-86, app/parser.py:85,288-291. Not protected.
- **Fix:**
  - For a rat, or any animal not known to cause neurotoxicity, with ptosis, speech_swallow, breathing or weakness, go to the snake path regardless of night/floor.
  - Add `we think|i thought|was it|looked like|long|black` to HEDGE.
  - Treat a `?` after the animal word as doubt.

**R2-11 (S2): The production self-updater has no gate or rollback, and there is no DB backup, during the judged window.**
- **Files:** deploy/cloud-config.yaml:41-52 (PROTECTED).
- **Fix (escalate):**
  - In the updater, after the pull, run `venv/bin/python -m pytest -q tests`.
  - Restart, then `curl /api/health`. On any failure, `git reset --hard $OLD` and restart.
  - Add a cron job: `sqlite3 dansh.db ".backup /srv/dansh/data/bk-$(date +%H).db"` plus a CSV export.
  - Simplest: disable the timer at code freeze.

**R2-12 (S2, security): Root updater running in a repo owned by the app user, with safe.directory set, gives app-to-root escalation through `.git/config` (`core.fsmonitor`).**
- **Files:** deploy/cloud-config.yaml:54-55 (PROTECTED).
- **Fix:** Keep the repo root-owned and read-only to `dansh`. Run the updater as a separate user, or drop the safe.directory line. Put the DB and salt (already in /srv/dansh/data) as the only dansh-writable paths.

**R2-13 (S2): Hinglish self-harm is not detected** (`main marna chahta hoon`, `mujhe jeena nahi hai`).
- **Files:** app/parser.py:90-91. Not protected.
- **Fix:** Add `marna chahta`, `marna chahti`, `jeena nahi`, `jaan de dunga/dungi`, `khudkushi`.

**R2-14 (S2, latent): An LLM "add" can lower the priority of 108.** `self_harm=True` from the model gives SUPPORT with calls `[14416, 112, 108]`.
- **Files:** app/llm.py:26-27,88-91; app/protocol.py:121-125,157. Not protected.
- **Fix:** Do not take `self_harm` (or `prevention`) from the model. Or, on any bite context, always put 108 first and keep 14416 second.

**R2-15 (S1): Content deltas against the STG** (protected app/content.py).
- `recovery_position` should say "left side" (STG p.8).
- `nil_by_mouth` cites p.8 for aspirin; that warning is on p.45, and alcohol is not in the STG.
- `other_bite` still has no anaphylaxis line for multiple bee stings with breathlessness.
- **Fix:** Human-reviewed wording change.

**R2-16 (S1): False alarms that hurt credibility with judges.**
- `my baby bit my finger`, `I bit my tongue`, `teeth marks from my toddler`, `two marks on his knee from the stairs`, `what should I keep at home for snakebite first aid`, `is there a snake helpline in Bihar`, `I pricked my finger while sewing`, and `cat scratched me, maybe infection` (which gets "don't wash").
- **Files:** app/parser.py (PERSON/BITE/UNKNOWN/THORN). Not protected.
- **Fix:**
  - A human biter (baby, toddler, I bit my) means OFF_TOPIC.
  - `first aid` or `helpline` with no person means INFO.
  - Add `scratch|scratched` to the biter verbs for an explicit animal.

**R2-17 (S1): Eval sets no longer discriminate (54/54).** No test covers R2-1..4, 10 or 13.
- **Files:** tests/ (not protected); eval_cases/ (PROTECTED for new files: needs human sign-off).
- **Fix:**
  - Freeze `/tmp/aud2/probe/fresh.json` as holdout3 before fixing, after a human signs off.
  - Add a fuzz that mixes symptom words with prevention words and a snake.

**R2-18 (S1): Deploy hygiene.**
- `ufw enable` is never run (cloud-config.yaml:87,99-100).
- Caddy runs as root, and its binary has no checksum (:69,75-86).
- A boot-log server left on :80 can block Caddy if the install fails.
- Dockerfile:14 trust default for PaaS.
- `_buckets.clear()` reset (main.py:55).
- **Files:** deploy/** (PROTECTED), Dockerfile, app/main.py.
- **Fix:** As described in each item above.

**R2-19 (S1): UX.**
- The "Dangerous choice" column is clipped at 360 px on /impact (impact.html:16-19).
- The /impact nav is English only.
- The plan language follows the UI language, not the message's language (app.js:165).
- /api/health has no git SHA.
- **Fix:**
  - Shorten the header to "Danger" or make the column wrap.
  - Send `lang: null` on the first consult so the detected language is used.
  - Add `"commit"` to /api/health.
