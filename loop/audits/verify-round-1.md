# Checker verdicts, audit round 1 (fix commits on top of ce65e33)

Checker ran: pytest at each commit snapshot (git archive to /tmp/chk_<sha>), both eval sets on a local server (HEAD :8098, baseline ce65e33 :8097 for comparison), table-B inputs and 75 fresh probes through parse()/decide() at baseline and at 673dabe, live API abuse probes, and a mutation test for F4. No files in /home/claude/dansh were edited. Servers stopped.

## Verdicts

- **6c107f1 fix(F1,F2,F3,F8): REJECT. Recommend human review (medical).** All 29 table-B inputs are fixed, but the HEDGE rule causes a new harm: a named dog, monkey, scorpion, bee or cat bite that also contains "kuch", "maybe", "I think", "not sure" or "shayad" now gets the snakebite plan. That plan says "Do NOT ... wash the bite" and drops the rabies wash and vaccine advice (10 of 10 probes, baseline was OTHER). The fix is also incomplete in the same class: chubh / two marks / two holes plus bachav or protect still gives INFO, and "khoon nahi jam/rok/thahar" still drops bleeding. It bundles 4 findings in one commit.
- **5d00833 fix(F4,F5,F6,F7) (+ unlabeled F12 headers): REJECT. Recommend human review (deploy and safety policy).** The F4 fix is correct: a mutation test catches the old code, and the test_core.py changes are legitimate. But the F7 body limit can be bypassed with a chunked body. The emergency /api/consult is rate-limited (429 on the 41st "cannot breathe" message in a minute). The Docker default FORWARDED_ALLOW_IPS=127.0.0.1 would put every PaaS user behind one IP. It bundles 5 findings.
- **6d545b8 fix(F11-code): APPROVE (low risk).** It is a one-line change to the default, and the fallback is the keyword parser, which still sends people to hospital. The httpx timeout applies to each phase, so the worst case is about 7.5-10 s, not the 2.5 s the comment says. The fallback rate needs to be watched in production.
- **673dabe fix(F12,F13): REJECT (low risk, trivial fix).** It adds an unclosed `<div>` in static/impact.js (8 open, 7 close), so the "Who took it" card ends up nested inside "By decision". The "CSP/HSTS" in the commit message is code that actually landed in 5d00833. F13 is only partly done: the Hindi on /impact covers the lede and 3 labels, and there is no tabpanel role.

## Evidence

### 1. Tests and evals
- pytest, `cd /home/claude/dansh && python3 -m pytest -q tests`:
  - at HEAD 601edfc: `83 passed in 9.56s`
  - each snapshot:
    - ce65e33: 40 passed
    - 6c107f1: 77 passed
    - 5d00833: 83 passed
    - 6d545b8: 83 passed
    - 673dabe: 83 passed
- Eval (main), `/tmp/chk1`: `{"cases": 22, "passed": 22, "false_safe": 0, "bite_cases_sent_to_hospital": 18, "bite_cases": 18, "under_triage": 0, "over_triage": 0, "controls_correct": 4, "controls": 4}`. Summary line: "18/18 bite cases sent to hospital (0 false safe)".
- Eval (holdout), `/tmp/chk2`: `{"cases": 16, "passed": 16, "false_safe": 0, "bite_cases_sent_to_hospital": 12, "bite_cases": 12, "under_triage": 0, "over_triage": 0, "controls_correct": 4, "controls": 4}`. Summary line: "12/12 bite cases sent to hospital (0 false safe)".
- **Caveat:** the baseline ce65e33 scores the same (22/22 and 16/16). The eval sets do not tell the fixes apart and catch none of the regressions below.

### 2. Gate
- **Fix commits:**
  - Files per commit: 3, 5, 1 and 4. All are under 10.
  - None touches eval_cases/**, eval_results/**, app/content.py, deploy/**, LICENSE or .env*.
  - The Dockerfile is not protected.
- **Process violation:** loop-constraints says "One finding per change", and it is broken:
  - 6c107f1 has 4 findings.
  - 5d00833 has 4 labeled findings plus the F12 headers, unlabeled.
  - 673dabe has 2 findings, and its CSP/HSTS claim describes code that is in 5d00833.
- **Later commits** (0d42bd0, 8443dfc, 601edfc):
  - None of them changed app/ or tests/ (`git diff 673dabe HEAD -- app tests` is empty).
  - **But 601edfc edits the protected deploy/cloud-config.yaml** (`OWNER` -> `acirema792`). This is the repo that the production self-updater pulls and `git reset --hard`s every 5 minutes. A human needs to confirm the owner and sign off.
  - 601edfc also commits loop/ledger.json, which marks F1-F13 "success". That record is not accurate (see below).
  - 0d42bd0 changes the public claim copy (58,000 -> "thousands"). I did not review it.

### 3. Cheating check
- No skip or xfail markers, and no assertion was removed (`git diff ce65e33 673dabe -- tests | grep '^-\s*assert'` is empty). test_llm_cannot_add_denied_flag was not touched.
- The test_core.py changes are legitimate:
  - `TestClient(app, client=(ip, 50000))` replaces the forged-XFF header, which was itself the F4 bug. Every assertion is kept, including `after - before == 5`.
  - `DANSH_MIN_PRE_SECS/POST_SECS=0` is needed, because TestClient finishes a check in milliseconds and every flow test would otherwise be excluded as too_fast. The timing filter is tested separately, with the real 20/30 s values, in test_integrity.py::test_f5.
  - `DANSH_RATE_PER_MIN=100000` is likewise test-only, and the rate limit has its own test.
- Mutation test: putting the XFF-trusting `_ip()` back makes `test_f4_forged_xff_does_not_bypass_device_cap` FAIL. So the new test is real.
- One weak test: `test_f7_big_bodies_rejected_and_answers_trimmed` sends the junk `answered` keys with `repeat=True`, so the logging path is never exercised and it asserts only HTTP 200. I checked the behaviour live instead: 20k junk keys were stored as `[]`.

### 4. Does each fix fix its finding?
- **Table B** (the inputs in round-1.md section B):
  - All 12 false-safe inputs now give POSSIBLE, URGENT or CRITICAL, with go_hospital and 108.
  - All 12 dropped-sign inputs now give CRITICAL with the flag kept.
  - The bare fragments ("khoon band nahi ho raha" with no snake) still give OFF_TOPIC with 112 and 108. That is acceptable.
  - Bee + breathless and scorpion + unconscious give OTHER with calls `['108','112']`. The content part was correctly left to a human.

**NEW problem A (introduced by 6c107f1, F8 HEDGE): animal bites lose the rabies advice and are told not to wash.**
- The rule `if (bite or other_animal) and any(HEDGE)` sets unknown_bite, and that makes R1 fall through to the snake protocol.
- The snake protocol includes `dont_cut_suck` ("Do NOT ... wash the bite") and leaves out `other_bite` (wash 15 min, rabies vaccine).
- Each of these was OTHER at baseline and is now POSSIBLE:
  - `kutte ne kaata, kuch karo`
  - `my dog bit me, I think it needs a vaccine`
  - `a dog bit my son, maybe rabies? what to do`
  - `bandar ne kaata, shayad rabies ka khatra hai`
  - `monkey bit me, not sure what to do`
  - `bichhu ne kaata, kuch upay batao`
  - `scorpion stung me, i think it is serious`
  - `a bee stung me, maybe allergic`
  - `cat scratched me, maybe infection`
- For dog and monkey bites this works directly against rabies first aid. "kuch karo" ("do something") is very common phrasing.
- Suggested direction: treat a hedge as doubt only when it qualifies the animal ("maybe a rat", "shayad chuha"), not anywhere in the message. Or, when an animal is named, show both the snake plan and the `other_bite` wash/rabies note, and drop "don't wash". That needs content work, so a human must review it.

**NEW problem B (6c107f1): false alarms on controls.** These are not unsafe for snakebite, but they hurt credibility, and some carry the wrong advice ("nil by mouth" for a vomiting, feverish patient):
- `how to protect from snake attack in the fields`: INFO -> URGENT ("attack")
- `why do snakes strike, how to avoid them`: INFO -> URGENT ("strike")
- `my father has fever and vomiting, he slept badly`: OFF_TOPIC -> CRITICAL ("slept" added to NIGHT_FLOOR)
- `my baby is drooling a lot, teething`: OFF_TOPIC -> CRITICAL ("drooling" goes to R3b)
- `I pricked my finger while sewing`, `kaanta chubh gaya pair me` (thorn): OFF_TOPIC -> POSSIBLE

**Residual false safes in the same class as F2/F3 (the fix is incomplete):**
- R2 checks `f.bite` but not `f.unknown_bite`. So the new UNKNOWN-only words, combined with a prevention word, still give INFO, with no go_hospital:
  - `pair me kuch chubh gaya, kaise bachav kare`
  - `बेटे को कुछ चुभ गया खेत में, बचाव कैसे करें`
  - `two marks on his leg, how to protect him from infection`
  - `my son has two holes on his foot, how to protect him`
- Suggested fix: change R2 to `not (f.bite or f.unknown_bite or ...)`.
- `a rat bit my son while sleeping on the floor, now he can't open his eyes` still gives OTHER. This is a krait picture blamed on a rat. It has 108 first, but the advice is the rabies text.

**Residual dropped danger signs (F1(c) is incomplete; these were also wrong at baseline). Each flag goes into `negated`, so the follow-up question is suppressed:**
- `saanp ne kaata, khoon nahi jam raha` ("blood not clotting", a classic viper sign): bleeding is denied, giving URGENT
- `khoon nahi rok pa rahe`, `khoon nahi thahar raha`, `ulti nahi thahar rahi`: denied
- `snake bite no ambulance bleeding a lot`: bleeding is denied by NEG_BEFORE across "ambulance"
- `snake bite, breathing is ok for now but getting worse` and `breathing is fine earlier but now he is gasping`: breathing is denied
- The HI_NEG_AFTER lookahead is a word blacklist (ruk, tham, band). A safer rule would deny only for the explicit `nahi aa raha / nahi hai / nahi hua` forms.

**Controls that are unchanged and correct:**
- `dog bit me`: OTHER
- `hello`: OFF_TOPIC
- `my child has a fever and cough, maybe flu`: OFF_TOPIC
- `how to prevent snakebite` and `saanp se bachav kaise kare`: INFO, now with 108
- `kuch samajh nahi aa raha`: OFF_TOPIC

**5d00833, live probes:**
- **F4:** fixed in code. With uvicorn 0.54 (the rightmost untrusted XFF entry wins) and Caddy on 127.0.0.1 (cloud-config), spoofing should fail. That has to be confirmed on the live deployment.
- **Docker default trust setting (risk):** with `FORWARDED_ALLOW_IPS=127.0.0.1` on a PaaS, every client resolves to the platform proxy IP. That would mean a device cap of 5 completions per day for all users together, and a single 40/min rate-limit bucket for everyone.
- **F5:** too_fast exclusion works (test_f5). The rule is published on /impact.
- **F6:** the state and role whitelists match the frontend lists exactly (34 of 34 states, 6 of 6 roles). The CSV guard is present.
- **F7:**
  - A 55 KB body with Content-Length gets 413.
  - **The same body sent with Transfer-Encoding: chunked gets past the limit** (404 from the handler).
  - Storage is now bounded: the DB size was unchanged after a chunked consult with 20k junk `answered` keys, and the stored flags were `[]`. The remaining risk is memory and CPU use from large bodies.
- **Rate limit on the emergency endpoint:** 45 consults of "snake bit my father, he cannot breathe" in under a minute gave 40 x 200, then 429. The client catches the error and shows the 108/112 fallback, but the plan is lost. Consider exempting /api/consult, or limiting only the learn/* endpoints. The eval runs (38 consults) are close to this limit.
- **F12:** CSP, HSTS, X-Frame-Options DENY and HEAD / 200 are served. No inline handlers or inline scripts remain in static/.

**673dabe:**
- The unclosed div noted in the verdict above.
- The `repeat` flag also suppresses logging of follow-up answers, so escalations are never logged.
- The language switch still re-POSTs, which is now unlogged but still uses a rate-limit token and, when enabled, an LLM call.

### 5. Risk and human review
- **6c107f1, MEDIUM-HIGH. Human review required.** This is medical routing: dog and monkey bites now get "don't wash" with no rabies advice, and the residual false safes and dropped signs remain. Whether animal bites should get the snake plan, and whether the `other_bite` note should be shown alongside it, is a medical content decision (content.py is protected).
- **5d00833, MEDIUM. Human review recommended.** Rate-limiting the emergency endpoint is a safety-policy decision, and the proxy trust setting depends on how the app is deployed. Both should be confirmed live.
- **601edfc, gate.** It edits a protected path (deploy/cloud-config.yaml) that controls which repo production pulls from. A human must confirm it.
- **The ledger** marks F1-F13 "success". It should be corrected to partial or failed for F1, F2/F3 (R2 gap), F7 (chunked bypass), F8 (regression) and F13 (markup bug).
