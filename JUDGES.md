# Review Dansh in five minutes

No account, key or install needed. Use a phone if you can: that's who it's for.
Add `?test=1` to any URL so your clicks are **not** counted in the impact numbers.

## 1. Emergency agent (90 seconds)

Open {{LIVE_URL}}/?test=1 and paste these messages one at a time:

| Paste this | What you should see |
|---|---|
| `papa ko saanp ne kaata, rassi baandh di` | Hindi answer, red "go to hospital now". A yellow correction about the rope **above** the steps. 108 button first. |
| `snake bit my brother, no swelling, no pain, he feels fine, can we stay home?` | Still "go to hospital now", plus the 24-hour observation step (kraits paralyse hours later). It never says "stay home". |
| `my son slept on the floor and woke up vomiting, eyes half closed, no bite mark` | **EMERGENCY**, "this could be a krait bite even with no wound", recovery position. |
| `saanp ne kaata, saans nahi aa rahi` | EMERGENCY. *"saans nahi aa rahi"* means "can't breathe". A naive negation parser would read it as "no breathing problem". |
| `dog bit me` | Not a snakebite: rabies-vaccine pointer, 108. The snakebite protocol does not fire. |

Then press **Yes** on "Any difficulty breathing?" under a normal bite. The level changes to EMERGENCY.
Open **"Why this advice?"** to see the exact rules that fired. Every line has a source chip such as `STG2017 p.9`; click it to open the Health Ministry PDF.

## 2. The 3-minute check (2 minutes)

Open {{LIVE_URL}}/check?test=1 and answer badly on purpose. You get a lesson (missed items first), then 6 *different* scenarios on the same decisions, then before/after scores and a WhatsApp share button.

## 3. The proof (90 seconds)

- **Field data:** {{LIVE_URL}}/impact shows the real people who completed the check, the share who chose a dangerous action before vs after, and per-decision results. Raw rows: `/api/impact/sessions.csv`. The exclusion rules (test traffic, device cap, too-fast) are listed on the page, with counts.
- **Safety benchmark:** [BENCHMARK-RESULTS.md](BENCHMARK-RESULTS.md). Expected answers are written before each run; misses are listed, not hidden.
- **Claims and their evidence:** [CLAIMS.md](CLAIMS.md) · criteria map: [EVIDENCE.md](EVIDENCE.md)

## Where each claim lives in the code

| Claim | Where |
|---|---|
| Every sentence comes from the guideline, with its page | `app/content.py` (`ITEMS`, `SOURCES`) |
| The rules decide; the model never writes advice | `app/protocol.py` `decide()`; `app/llm.py` `merge()` |
| A possible bite always gets 108 + hospital + never-dos | `app/protocol.py` `check_invariants()`, enforced on every API response in `app/main.py` |
| The LLM can only add danger signs | `app/llm.py` `merge()`; `tests/test_core.py::test_llm_merge_only_adds` |
| Hindi "nahi" handled safely | `app/parser.py` `_negated()`; `tests/test_audit_r1.py::test_f1_flag_kept` |
| Test traffic is excluded from impact | `app/main.py` `_is_test()`; `app/store.py` `completed_sessions()`; `tests/test_core.py::test_learn_flow_and_impact_excludes_test` |
| Counterbalanced forms | `app/quiz.py` `assign_forms()` |
| Impact numbers can't be stuffed | `tests/test_integrity.py` |
