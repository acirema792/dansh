# Claims and their evidence

Evidence tiers:
- **REPRODUCIBLE:** a script or test in this repo produces it.
- **VERIFIED-LIVE:** you can see it on the deployment now.
- **SOURCED:** a published source, linked.
- **NOT-CLAIMED:** stated so nobody reads it in.

| Claim | Tier | Evidence |
|---|---|---|
| Every possible snakebite gets "call 108 + government hospital + never tourniquet / cut / healer" | REPRODUCIBLE | `check_invariants()` runs on every API answer; `tests/test_core.py::test_fuzz_invariants` (3,000 messages); `tests/test_audit_r1.py::test_fuzz_snake_plus_bite_word_never_out_of_protocol` (2,000) |
| 0 false "safe" on the held-out scenario set | REPRODUCIBLE · VERIFIED-LIVE | `eval_cases/holdout.yaml`, `scripts/run_eval.py`, [BENCHMARK-RESULTS.md](BENCHMARK-RESULTS.md) |
| Advice text follows MoHFW STG 2017, page by page | SOURCED | `app/content.py`. Each item has `src` and `page`; checked against the PDF by an independent auditor (`loop/audits/round-1.md`, section B) |
| The language model never writes advice and can only add danger signs | REPRODUCIBLE | `app/llm.py::merge`, `tests/test_core.py::test_llm_merge_only_adds`, `test_llm_cannot_add_denied_flag` |
| Before/after numbers on /impact are from real people | VERIFIED-LIVE | `/impact`, `/api/impact`, `/api/impact/sessions.csv`. Exclusions are listed with counts. |
| Impact numbers exclude test traffic, device floods and too-fast completions | REPRODUCIBLE | `tests/test_integrity.py`, `tests/test_core.py::test_device_cap` |
| No personal data stored | REPRODUCIBLE | `app/store.py` schema: no message text, no IP, no name or phone |
| ~58,000 deaths a year | SOURCED (contested) | eLife 2020. A 2025 ICMR survey found far lower mortality in its districts; both are shown in the README. |
| Dansh reduces deaths | **NOT-CLAIMED** | We measure decisions immediately after a lesson, not outcomes. |
| Dansh diagnoses or identifies snakes | **NOT-CLAIMED** | It never diagnoses; it always sends to hospital. |
| Hospital list guarantees antivenom stock | **NOT-CLAIMED** | OpenStreetMap has no stock data. The app says to prefer government hospitals and to call ahead. |
| Clinically validated | **NOT-CLAIMED** | Not reviewed by a clinician yet; this is the first next step. |
