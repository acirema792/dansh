# Loop state

Round: 2 (round-2 fixes committed; verifier pass 3 running)
Scores: round 1 = 5.4, round 2 = 6.5

## Baseline tripwires
- pytest: 40 -> 114 passed (HEAD)
- eval cases.yaml 22/22, holdout.yaml 16/16 (local), 0 false safe
- Live: https://65-20-73-107.sslip.io (Vultr Mumbai, created 2026-11-13 15:40 UTC), serving 0a69d76 at 17:25 UTC
- pytest: 214 passed

## Open findings
- F9/F10 judge docs: README/JUDGES/CLAIMS/EVIDENCE written; BENCHMARK-RESULTS + IMPACT-SNAPSHOT pending live run
- F11 deploy: no tested-update gate / rollback in self-updater (protected: deploy/**)
- F14 misc

## Escalations (for the person)
1. content.py wording: bee/scorpion sting + breathlessness currently gets the dog-bite/rabies text (with 108 first).
   Suggest a separate "allergic reaction / scorpion" item. Protected path (medical text).
2. tests/test_core.py::test_llm_cannot_add_denied_flag asserts the model cannot re-add a denied sign.
   The safer behaviour is to let it; changing it touches a test assertion.
3. Test changes after verifier round 1:
   - tests/test_audit_r1.py fuzz narrowing was REVERTED in d185b66 after verifier 1b showed it hid a defect.
   - tests/test_integrity.py::test_f7_rate_limit retargeted to /api/learn/start (verifier 1b: legitimate).
   - tests/test_verify_r1.py V1 cases ('kutte ne kaata, kuch karo' etc.) kept as OTHER via HEDGE_IGNORE.
4. deploy/cloud-config.yaml was edited (repo URL, early ufw). Needs your confirmation per gate.

5. Deploy hardening (R2-11/12, protected deploy/**): self-updater has no test gate/rollback/DB backup, and root runs git
   in an app-owned dir. Vultr automatic backups are ON (daily image) as partial mitigation.
6. holdout2.yaml header says '~16:20 UTC'; actual commit 16:07:42 (documented in BENCHMARK-RESULTS.md; file frozen).

## Rulings
(none yet)
