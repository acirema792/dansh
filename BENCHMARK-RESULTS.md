# Safety benchmark

**Headline:** on a held-out set written before its first run (set 2, 16 messages, live site): **12/12 bite messages sent to hospital, 0 false "safe"**, 14/16 exact.
There were two misses, both shown below and fixed afterwards. The held-out score stays as recorded.

## How it works

- Each scenario is a message someone might type (English, Hindi in Devanagari, or Hinglish) with the **expected outcome written down first**: the urgency level, plan items that must appear, and items that must not.
- Expectation files are never edited after a run. When a run shows a miss, the fix comes with a new unit test, and the score of that run stays as it was.
- **Safety checks applied to every bite message:** it must reach a hospital level (POSSIBLE / URGENT / CRITICAL), and the plan must contain 108, go-to-hospital and the three never-dos. Any bite message that doesn't is a **false safe**.
- **Controls:** dog, scorpion, bee and monkey bites, prevention questions, a fever, a greeting. These must *not* trigger the snakebite protocol.
- Runner: `scripts/run_eval.py <url> --cases <file>`. The live runs were sent from a browser to the live site, because the build machine can't reach it, and scored with the same code. Raw bundles are in `eval_results/`.

## Every run, in order

| # | When (UTC) | Set | Where | Exact | Bites → hospital | False safe | Under-triage | Controls | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 13 Nov 02:32 | `cases.yaml` (22) | local | 19/22 | 18/18 | **0** | 0 | 4/4 | 3 misses: krait with "no bite mark", "khoon choosa" read as bleeding, "6 year old" not read as a child. Fixed and pinned by tests. |
| 1 | 13 Nov 02:33 | `holdout.yaml` (16), first run | local | 15/16 | 12/12 | **0** | 0 | 4/4 | "yesterday" not read as a time. Fixed afterwards. |
| – | 13 Nov 03:00–15:00 | independent audit + verifier | – | – | – | – | – | – | The audit found **real false safes the sets above missed** (e.g. "snake attack on my son, how to protect him", "fang marks", "saans nahi aa rahi" read as "no breathing problem"). All are now regression tests: `tests/test_audit_r1.py`, `tests/test_verify_r1.py`. |
| 2 | 13 Nov 16:07 | `cases.yaml` (22) | **live** | 22/22 | 18/18 | **0** | 0 | 4/4 | After fixes; no longer held out. |
| 3 | 13 Nov 16:07 | `holdout.yaml` (16) | **live** | 16/16 | 12/12 | **0** | 0 | 4/4 | After fixes; no longer held out. |
| 4 | 13 Nov 16:08 | **`holdout2.yaml` (16), first run** | **live** | **14/16** | **12/12** | **0** | **1** | 3/4 | Under-triage: "now he says he sees double" (krait, double vision) got URGENT, not CRITICAL. It still went to hospital. False alarm: "keep snakes out of my house?" got the bite plan. Both fixed afterwards (`test_h2_*`). |

Full tables: [`eval_results/live-holdout2-run1.md`](eval_results/live-holdout2-run1.md) · [`live-holdout.md`](eval_results/live-holdout.md) · [`live-cases.md`](eval_results/live-cases.md) · [`run-0-local-before-fixes.md`](eval_results/run-0-local-before-fixes.md) · [`holdout-run-1-local.md`](eval_results/holdout-run-1-local.md)

Times are the `ran_at` values recorded in each bundle. The header comment in `holdout2.yaml` says "~16:20 UTC", which is wrong: git shows the file was committed at 16:07:42 and first run at 16:08:22. The file is not edited, because expectation files are frozen.

## Audit-found inputs (adversarial set)

Two independent audit rounds and five verifier passes wrote and labelled adversarial messages, and many of them broke earlier versions. Their labelled corpus is `tests/data/adversarial.json`: **992 messages**, including the held-out sets of verifier round 3 (101), round 4 (175, plus a 52-message probe grid) and round 5 (166, plus a 51-message grid). `tests/test_adversarial.py` asserts **0 false safes, 0 under-triage, and a crisis line for self-harm**.

Result at the time of writing: **969/992 as labelled, 0 false safes, 0 under-triage**. All 23 differences are over-triage: thorn, needle and nail pricks, figures of speech ("the cold wind bites", "love bite"), snake sightings, and bee or scorpion stings with body-wide signs, which get the full hospital plan.

**Held-out results from the verifiers, recorded before the fixes that followed them:**
- Verifier round 5 wrote 166 new messages against commit ccb9302. Result: **15 false safes (9 not arguable)** and 30 under-triaged danger signs (`loop/audits/verify-round-5.md`). The causes were an animal-as-biter pattern that still read "got bitten while milking the cow" as a cow bite, a "did not bite, all fine" rule that ignored a later scratch or symptom, and danger signs matched only as exact phrases. The fix reads the grammar (the animal must be the subject of the bite, or named with "by"), adds spelling-tolerant patterns for each danger sign, and adds a catch-all: a body-wide change after a bite that matches no listed sign ("bachha nidhaal ho gaya", "he keeps nodding off") is CRITICAL.
- Verifier round 4 wrote 175 new messages against commit 931552f. Result: **30 false safes** and 32 under-triaged. Before any fix, the corpus with its messages added stood at 78 false safes and 32 under-triaged out of 775. Its report is `loop/audits/verify-round-4.md`.
- Verifier round 3 wrote 101 new messages against commit d500cbf. Result: **25 false safes**, 15 under-triaged, 10 false alarms (`loop/audits/verify-round-3.md`).
- Verifier round 2 (`verify-round-2.md`) and round 1b (`verify-round-1b.md`) found earlier regressions the same way.

Each round found false safes that the previous fixes had created. Every rule written to *suppress* a false alarm opened a new gap. Round 4 traced most of its 30 to one rule: any animal word anywhere in the message ("bitten while milking the **cow**", "**rat** 2 baje", which is Hinglish for *raat*, night) made the bite "another animal's" and switched the safety net off. The fix after round 4 changes the routing, not just the word lists:
- another animal is out of scope only when the message says it is the biter ("dog bit me", "kutte ne kaata", "bitten by a stray dog");
- any bite word with a body part, a family member or an outdoor or night setting is a possible snakebite;
- a snake doing something to someone ("saanp ne maara", "cobra spat in his eyes") counts as contact;
- "kya kare" / "what to do" alone no longer makes a message a general question.

These rules were fixed *against* this corpus, so it is a regression test, not a held-out score. The held-out measure is each verifier's fresh probe set, reported in `loop/audits/`. Scenario set 2 (holdout2) went from 14/16 to 16/16 after its two misses were fixed. The live 14/16 is the held-out figure.

## What this does and doesn't show

- It shows the rules behave as designed on realistic, varied phrasings, including Hindi negation traps. It also shows that in every run, no bite message was ever left without a hospital referral.
- The scenario sets are small (16–22 each) and were written by the builders. The independent audit found failures they missed, which is why the audit's inputs became permanent tests. A clinician-written scenario set is the next step (see [CLAIMS.md](CLAIMS.md)).
- Larger property tests: 3,000 random messages (`test_fuzz_invariants`) and 2,000 snake + bite-word messages (`test_fuzz_snake_plus_bite_word_never_out_of_protocol`) never produced a bite plan without the safety items.
