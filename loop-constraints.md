# Loop constraints (binding, read at the start of every round)

- Target OVERALL_SCORE 9.0, max 3 rounds. Code freeze: **2026-11-14 08:00 UTC**; after that only docs/tests.
- One finding per change. Smallest diff that fixes the root cause. No drive-by refactors.
- Never disable, skip or loosen a test; never delete an assertion.
- Max 3 attempts per finding; stop early if the same error repeats twice.
- Protected paths (escalate, never auto-edit): see gate.yaml. They back published claims
  (eval expectations, recorded results) or medical guidance text.
- Never fabricate or alter impact data. Never count test traffic as real users.
- Safety invariant: no change may make any possible-snakebite input produce advice other than "go to hospital".
- Push/deploy only after telling the person.
