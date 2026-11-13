# Dansh audit, round 1 (independent, read-only)

Date: 2026-11-13 ~02:40 UTC. Auditor ran: `pytest -q tests` (40 passed), ~180 hand-written probe messages through `parse()`/`decide()`, a local server on :8099 (`DANSH_DB=/tmp/audit/audit.db`) with API abuse probes, and headless Chrome screenshots at 360x740. The cited STG 2017 PDF was read through WebFetch to check the content. Scratch files are in /tmp/audit.

I could not compare against other Health submissions: the GitHub issues API and pages are blocked from this session (gh GraphQL 403, REST "repo not enabled", WebFetch not allowlisted).

---

## Scores

### A. Event fit: 4.5 / 10
- **Problem size (rubric 1).** The only figure is "58,000 deaths/yr". It appears in `static/index.html:9`, `static/app.js:31,46` and in the share text, and its source is `content.py:20-23` (Suraweera et al., eLife 2020). There is no judge-facing write-up of how many people are affected: bites per year (~1.2 M deaths over 2000-19, about 2.8 M bites/yr), rural/farmer share, or the states with the highest burden.
- **Severity (rubric 2).** No numbers on disability, amputations or economic loss appear anywhere in the repo.
- **Solution quality (rubric 3).** The design is strong: the protocol is deterministic, each line of advice cites the STG with a page number, the LLM is monotone (it can only add), and there is a rule trace (`protocol.py:318-431`). But see the false-safe cases under B.
- **Proven impact (rubric 4).** The infrastructure is good: counterbalanced A/B forms (`quiz.py:147-149`), a dangerous-choice metric, a public JSON and CSV (`main.py:256-272`), and a stated limits paragraph (`impact.html:45`). However:
  - There is no deployment and there are zero real rows.
  - No distribution plan is written down. The `src` tag exists but no campaign uses it.
  - There is no retention or follow-up measure.
- **Ergonomics and eligibility gaps:**
  - No README.
  - The footer GitHub link points to `https://github.com/` (`app.js:8`).
  - `deploy/cloud-config.yaml:11` still has `OWNER` as a placeholder.
  - `eval_cases/cases.yaml:3` cites `BENCHMARK-RESULTS.md`, which does not exist.
  - There is no demo link or video, and no AgentFoundry mention.

### B. Medical safety and correctness: 6 / 10
The architecture is safe by construction: every POSSIBLE/URGENT/CRITICAL plan has `go_hospital` and `call_108`, `check_invariants` is enforced at `main.py:81-83`, and a "No" answer cannot remove a stated symptom (`protocol.py:327`). Probing still found real false safes and dropped danger signs.

**FALSE SAFE (a real bite gets no hospital plan):**

| Input | Got |
|---|---|
| `a snake got my son, how do I protect him` | INFO (prevention tips) |
| `snake attack on my son, how to protect him now` | INFO |
| `saanp ne hamla kiya, bachav kaise kare` | INFO |
| `fang marks` / `my child was playing near the woodpile and now has fang marks` | OFF_TOPIC |
| `my husband can't open his eyes and is drooling, slept outside` (krait picture) | OFF_TOPIC |
| `snakbite`, `snakebit` (typos) | OFF_TOPIC |
| `mere pair me kuch chubh gaya, khet me` | OFF_TOPIC |
| `while chasing a rat, I was bitten on the hand in the dark` | OTHER (rabies advice) |
| `bitten while cleaning the cowshed, maybe a rat` | OTHER |
| `dog barked at something, then my son screamed, two marks on leg` | OTHER |

**DANGER SIGN DROPPED (CRITICAL becomes URGENT; the sign is also put in `negated`, so the follow-up question is suppressed and the LLM is blocked from re-adding it, `llm.py:265`):**

| Input | Flag lost | Cause |
|---|---|---|
| `saanp ne kaata, koi madad karo saans nahi aa rahi` ("someone help, can't breathe") | breathing | `koi` in NEG_BEFORE `parser.py:170` |
| `साँप ने काटा, कोई मदद करो सांस नहीं आ रही` | breathing | same |
| `saanp ne kaata, saans theek nahi hai` / `सांस ठीक नहीं है` ("breathing not OK") | breathing | NORMAL_AFTER `parser.py:171` ignores a following nahi |
| `snake bit him, breathing not fine` / `breathing fast, not fine` | breathing | same |
| `saanp ne kaata, kamzori theek nahi ho rahi` | weakness | same |
| `snake bit him, no idea why breathing is hard` | breathing | NEG_BEFORE 2-word window |
| `saanp ne kaata, khoon nahi ruk raha` ("bleeding won't stop") | bleeding | HI_NEG_AFTER `parser.py:172,187` |
| `khoon band nahi ho raha`, `ulti nahi ruk rahi`, `vomiting nahi ruk rahi` | bleeding / vomiting | same |

**Missed danger-sign vocabulary (stays URGENT; still sent to hospital):**
- `unable to swallow`, `slurring`, `urine is red`, `peshab laal`
- `collapsed`, `passed out`, `convulsions`, `fits`, `jhatke`
- `sleepy`, `neend aa rahi`, `gasping`, `haanf raha`, `chest tight`
- `aankhen jhuk rahi`, `palke bhaari`

**Other-animal path with danger signs.** `bee stings all over, he is breathless` returns OTHER with the dog-bite and rabies text. `bichhu ne kaata, bachcha behosh` returns OTHER. The `other_bite` text (`content.py:189-193`) has no anaphylaxis line and does not tell a child with a scorpion sting to call 108.

**Content check against the STG 2017 PDF.** These items match what I could read: "Do not wash the wound" (p.9), tourniquet causes gangrene (p.9), "~70% non-venomous" (p.7), 24 h observation (p.10), krait presents in the morning with no bite marks (p.17), nil by mouth (p.8), traditional remedies have no proven benefit (p.8). Differences and gaps:
- The STG specifies the *left* side for the recovery position; ours says "on their side".
- `cobra spat in his eyes` gets limb-immobilisation advice and no eye irrigation.
- Hinglish `main marna chahta hoon` is not detected as self-harm; only the Devanagari form is (`parser.py:81-82`).
- `kal` always means "yesterday", so a message saying "tomorrow" adds `late_note` (`parser.py:194`).

### C. Impact-measurement integrity: 4.5 / 10
- **The device cap can be bypassed (confirmed).** `_ip()` trusts the first entry of `X-Forwarded-For` (`main.py:42-44`). 20 scripted completions with forged XFF and 0/6 → 6/6 answers were all counted: the public page showed 25 completed, 0% → 100%, 25 improved, 25 shared. The test suite relies on the same spoof (`tests/test_core.py:169,178,186`). The Dockerfile trusts every forwarder (`--forwarded-allow-ips "*"`, `Dockerfile:13`).
- **No plausibility filter.** There is no minimum time-on-task, and `created_at`/`completed_at` exist but are unused. The correct answers are public in `quiz.py`. A whole completion takes milliseconds.
- **Public free text.** `state`, `role` and `src` are free text, shown on /impact (escaped, but they show `<img…>` or "visit evil.example") and in the CSV, where formula injection is possible (`main.py:141-143,96`; `impact.html:78`).
- **Easy inflation.** `shared` can be set for any session id, with no completion check (`main.py:181-184`). `started` can be inflated without limit.
- **Developer traffic counts unless they add `?test=1`.** Yet `impact.html:35` claims "Test runs (including the developers')… are excluded". The language toggle re-POSTs `/api/consult` (`app.js:118`), so consult counts are doubled.
- **Methodology wording overclaims.** `impact.html:44` says "A device that completes more than 5 checks… only counts for its first 5". That is not true while XFF is spoofable, and the cap resets at UTC midnight because of the daily hash.
- **Privacy is good.** There is no message text, no raw IP (salted, day-rotated hash, `store.py:386-388`) and no device column in the CSV. One gap: when the LLM is on, the message goes to Anthropic, and the page does not say so.

### D. Security: 5.5 / 10
- **Good:**
  - Every server string is passed through `esc()` before `innerHTML` (`app.js` renderPlan, hospital names, impact `kv()`).
  - `message` is capped at 2000 characters, and `lang` is validated by regex.
  - The regexes ran in linear time on 2000-character adversarial inputs (≤0.13 s).
- **Unbounded stored payloads (confirmed):**
  - One `/api/learn/pre` call with a 20 MB `answers` dict grew the DB from 0 to 20.3 MB (`main.py:107-109`, `store.py:405`).
  - `/api/consult` stores every truthy `answered` key, unfiltered: 638 KB of junk flags from one request (`main.py:85`).
- **No rate limiting anywhere.** This allows DB growth and, with the LLM on, unlimited paid API calls.
- **Missing headers:** no CSP, no `frame-ancestors` / X-Frame-Options, no HSTS (`main.py:32-39`). The inline `onfocus=` at `app.js:265` blocks a strict CSP.
- CSV formula injection: see C.

### E. Reliability and deploy: 6 / 10
- **Good:**
  - Top-level requirements are pinned (`requirements.txt`).
  - The Dockerfile has a healthcheck and runs as a non-root user.
  - cloud-config runs uvicorn on 127.0.0.1 behind Caddy with proxy-headers trusted only from 127.0.0.1.
  - If Overpass fails, the page falls back to a Maps search link with a 16 s abort (`app.js`).
  - If the LLM fails, the keywords are used (`llm.py:249-252`).
  - If the API fails, the client shows 108/112 (`app.js` runConsult catch).
- **Weak:**
  - The LLM call is synchronous with a 6 s timeout on the emergency path (`llm.py:205`).
  - The self-updater does `git reset --hard` and restarts every 5 minutes, with no test gate and no rollback (`cloud-config.yaml:41-52`).
  - The Caddy binary is downloaded without checksum verification (`:69`).
  - The SQLite DB has no backup or export. On an ephemeral PaaS the Docker `/data` volume can be wiped, and that is the "proven impact" evidence.
  - `HEAD /` returns 405, which breaks some uptime monitors.
  - The install log is world-readable on :80 during boot.
  - Nothing is deployed yet.

### F. Testing: 6.5 / 10
- **The 40 tests are real and meaningful:**
  - invariants
  - a 3000-message fuzz
  - monotone levels over combinations of facts
  - the LLM merge can only add
  - API flow, cap and CSV
  - eval-miss regressions
- **Weak:**
  - There are no adversarial negation tests, which is why the F1 class went unnoticed.
  - `test_device_cap` enshrines the XFF spoof.
  - The eval sets are small: 22 + 16 cases, written by the same team.
  - Evals were run only against localhost. The LLM path has never been evaluated.
  - There are no frontend or JS tests.
  - The fuzz only asserts invariants for `snake and bite`. It never checks that "bite-ish" words without the literal word avoid OFF_TOPIC or INFO.

### G. Code quality and UX: 7 / 10
- **Good:**
  - The code is small and readable.
  - All UI strings exist in both Hindi and English, and Devanagari renders correctly (screenshot `/tmp/audit/m_hi_top.png`).
  - No horizontal overflow on `/` at 360 px.
  - The red 108 call bar, large tap targets, `prefers-reduced-motion`, and `aria-live` on the plan.
- **Weak:**
  - `/impact` is English-only and overflows by 4 px at 360 px.
  - In Hindi the header tabs wrap to three lines ("3 मिनट जाँच").
  - The test banner is not re-translated when the language changes (`app.js:283`).
  - `role=tab` has no `aria-controls` or tabpanel.
  - The `GH` placeholder (`app.js:8-9`) is dead code until `data-repo` is set.
  - Switching language re-runs and re-logs the consult.

**Weighted:** A 4.5×.30 + B 6×.25 + C 4.5×.15 + D 5.5×.10 + E 6×.10 + F 6.5×.05 + G 7×.05 = 5.35

OVERALL_SCORE=5.4

---

## Findings (prioritised)

**F1 (S1): Negation logic drops real danger signs, and the LLM cannot restore them.**
- **Files:** app/parser.py:170-191, app/llm.py:265, tests/test_core.py. Not protected.
- **Fix:**
  - (a) Drop `koi`/`कोई` from NEG_BEFORE, or require it to be directly adjacent (0 words between) and the window not to cross `,`/`.`.
  - (b) In `_negated`, do not treat the sign as denied when NORMAL_AFTER matches but `nahi|nahin|not|na|नहीं` follows within two tokens, or `not` precedes the normal-word.
  - (c) For HI_NEG_AFTER, do not deny when the next token after nahi/band is `ruk|ruka|rukta|tham|band|रुक|थम|बंद`.
  - (d) In `llm.merge`, let the model add a flag even if it is in `base.negated`. That is the more-care direction; remove it from `negated` when added. Update `test_llm_cannot_add_denied_flag` only with human sign-off: it currently asserts a less-safe behaviour, and the loop rules forbid loosening a test.
  - Add parametrised tests with every input in the B table.

**F2 (S1): A prevention question with a snake but no literal bite word gives INFO.**
- **Files:** app/protocol.py:350, app/parser.py:65 (BITE list). Not protected.
- **Fix:**
  - Add `attack, attacked, struck, strike, hamla, got my, fang, fangs, dasa liya` to the bite or attack vocabulary.
  - In R2, require `not f.snake or no person word` (child, son, father, my …), or simply add `calls=["108"]` to the INFO plan so a call button is always present.
  - Add the three INFO inputs from the B table as tests.

**F3 (S1): OFF_TOPIC for bite-mark, typo and krait-sign phrasings.**
- **Files:** app/parser.py:62-106, app/protocol.py:358-367. Not protected.
- **Fix:**
  - Add `fang`, `fang marks`, `two marks`, `snakbite`, `snakebit`, `snek`, `snak`, `chubh` to the bite or unknown-bite lists.
  - Make the ptosis/swallow patterns allow a pronoun: `can'?t open (his|her|their)? ?eyes`, `unable to swallow`, `drool`.
  - In R3, when any red flag is present but there is no stated cause, return calls `["108","112"]`, not just 112, or treat ptosis, speech or weakness at night as R3b.

**F4 (S1, impact integrity): The device cap can be bypassed with a forged X-Forwarded-For (verified).**
- **Files:** app/main.py:42-44, Dockerfile:13 (not protected), tests/test_core.py:169-191.
- **Fix:**
  - `_ip()` should return `request.client.host` only. Uvicorn `--proxy-headers` with a specific `--forwarded-allow-ips` already resolves the real client.
  - In the Dockerfile, set the trusted IPs per platform, not `*`.
  - Rewrite the tests to vary the client with `TestClient(app, client=("10.9.9.9", 1))` and keep every assertion.

**F5 (S2): No plausibility filter on completions.** A scripted 0 → 6 completion takes milliseconds.
- **Files:** app/main.py:146-166, app/store.py. Not protected.
- **Fix:**
  - Store `pre_at`. Mark the session as excluded (a new `excluded_reason` column, or `is_test=1`) if `pre_at - created_at < 20 s` or `completed_at - pre_at < 30 s`.
  - Publish the rule and the excluded count on /impact.
  - Add a per-IP limit on `/api/learn/start`.

**F6 (S2): Free-text state, role and src are published and exported to CSV.**
- **Files:** app/main.py:96,141-143,266-271. Not protected.
- **Fix:**
  - Whitelist state against the frontend STATES list and role against the six option values; otherwise store null.
  - Restrict `src` to `^[a-z0-9_-]{0,24}$`.
  - Prefix CSV cells that start with `= + - @` with `'`.

**F7 (S2): Unbounded request dicts are persisted, so a single request can bloat the DB (verified: 20 MB).**
- **Files:** app/main.py:63,85,108,132; app/store.py:405,413. Not protected.
- **Fix:**
  - Store only `{c: answers[c] for c in quiz.ORDER}` with 1-character option ids.
  - Log only `answered` keys that are in RED_FLAGS.
  - Reject bodies over about 16 KB (a middleware check on `content-length`).
  - Add a simple in-memory token bucket per IP on the POST endpoints.

**F8 (S2): Other-animal routing.**
- **Problems:**
  - Hedged mentions (`maybe a rat`, `dog barked at something… two marks`, `chasing a rat… bitten in the dark`) give OTHER.
  - Danger signs with an animal (bee + breathless, scorpion + child unconscious) get the rabies text.
- **Files:** app/protocol.py:343-347, app/parser.py:233-237 (not protected); app/content.py:189-193 (PROTECTED, wording needs human review).
- **Fix:**
  - In code: if a hedge word is present (`maybe, shayad, or, ya, not sure, pata nahi, something, kisi`), set `unknown_bite=True`, which gives the snake protocol.
  - If flags are present on the OTHER path, put 108 first and add `critical`-style wording. That needs a new content item, so escalate.
  - Escalate a bee/anaphylaxis line and an "eyes: rinse with plenty of water" line for spitting cobra to the human.

**F9 (S2, event fit): Judge-facing documentation is missing. Must be written before submission.**
- **Files:** new `README.md`, `docs/` (or `JUDGES.md`), `BENCHMARK-RESULTS.md` (referenced by the protected `cases.yaml:3`), `app.js:8` repo URL, `cloud-config.yaml:11` (PROTECTED).
- **The README must contain:**
  - Demo URL plus 90 s video, the live /impact link and the CSV link.
  - A one-paragraph problem statement with sourced size: about 58,000 deaths/yr and about 1.2 M deaths 2000-19 (eLife 2020); bites per year; who is bitten (farmers, children, poor rural households); the WHO/NAP-SE goal to halve deaths by 2030.
  - Sourced severity: disabilities and amputations, household economic loss and catastrophic spending, and the share of deaths before reaching hospital or after going to traditional healers.
  - The safety architecture: deterministic engine, monotone LLM, invariants, rule trace.
  - Eval results with their date and the false-safe count, including the held-out set.
  - Impact methodology and its limits.
  - A privacy statement, including that the LLM is a sub-processor when enabled.
  - How to run, test and deploy; the licence; "Built in AgentFoundry".
  - A 3-step judge walkthrough with copy-paste example inputs in English, Hindi and Hinglish.
- **BENCHMARK-RESULTS.md** must list every miss honestly (including this audit's false safes and the fixes) and keep the expectations frozen.

**F10 (S2, rubric 4): No field data yet, and no distribution plan.**
- **Files:** docs; app/main.py (an operator-exclusion cookie). Not protected.
- **Fix:**
  - Deploy now.
  - Run named, `src`-tagged campaigns (ASHA WhatsApp groups, a school or college class, farmer groups) and report each by `src`.
  - Exclude developer traffic with a one-time `/optout?k=TOKEN` that sets a cookie, rather than relying on `?test=1`.
  - Publish a dated CSV snapshot in the repo before judging.
  - Optionally add a 7-day re-check link to measure retention.

**F11 (S2): Data durability and deploy safety.**
- **Files:** deploy/cloud-config.yaml (PROTECTED), Dockerfile, app/llm.py:205.
- **Fix (escalate the deploy parts):**
  - Nightly `sqlite3 .backup` plus a CSV export off the box.
  - The updater should run `pytest -q` and check `/api/health` after restart, rolling back to OLD on failure.
  - Verify the Caddy checksum.
  - In code: lower `DANSH_LLM_TIMEOUT` to about 2.5 s. Better, return the keyword plan immediately and let the LLM only escalate on a follow-up call.

**F12 (S3): Security headers.**
- **Files:** app/main.py:32-39, static/app.js:265. Not protected.
- **Fix:**
  - Add `Content-Security-Policy: default-src 'self'; connect-src 'self' https://overpass-api.de; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'`.
  - Add `Strict-Transport-Security`.
  - Replace the inline `onfocus` with addEventListener.
  - Allow HEAD on `/`.

**F13 (S3): UX and i18n polish.**
- **Files:** static/impact.html, static/app.js:118,283, static/style.css. Not protected.
- **Fix:**
  - Translate /impact into Hindi (or make it bilingual).
  - Fix the 4 px overflow (`table{table-layout:fixed}` or a scroll wrapper).
  - Shorten the Hindi tab labels.
  - Re-render the test banner in `applyLang`.
  - On language toggle, re-render from the cached plan instead of re-POSTing, or send `x-dansh-test` so it is not double-counted.
  - Add `aria-controls` to the tabs.

**F14 (S3): Test and eval gaps.**
- **Files:** tests/test_core.py (not protected); eval_cases/** (PROTECTED: a new adversarial held-out file needs human sign-off).
- **Fix:**
  - Add a regression test for every F1, F2 and F3 input.
  - Add a fuzz assertion that any message containing a bite or attack word plus a snake word, or a fang/bite-mark word, never returns OFF_TOPIC, INFO or OTHER.
  - Add an LLM-path eval (recorded) once a key is available.
  - Freeze an adversarial held-out file (negations, typos, hedged animals) before fixing.

---

## Can only be verified on the live deployment
- That Caddy overwrites the client-supplied `X-Forwarded-For` and that `request.client.host` resolves to the real client behind it (`--forwarded-allow-ips 127.0.0.1`). Different PaaS proxies behave differently.
- HTTPS on sslip.io. Geolocation and the mic only work in a secure context.
- Overpass reachability and latency from Indian mobile networks; the quality of hospital results in rural districts.
- LLM latency and fallback rate in production, and `llm_model` in `/api/health`.
- SQLite durability across redeploys and self-updates; whether the salt file persists, since the device hash otherwise changes.
- Real `/api/impact` numbers: sample size, A→B vs B→A balance, the per-`src` split, and the share rate.
- Mobile rendering on low-end Android with system Devanagari fonts (Noto is not bundled; check fallback), and WhatsApp share-link previews (og tags).
- Running `scripts/run_eval.py` against the public URL, and the `latest.md` it writes.
