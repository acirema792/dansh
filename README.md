# Dansh · दंश: the first 30 minutes after a snakebite

**Live:** {{LIVE_URL}} · **Live impact data:** {{LIVE_URL}}/impact · **Review in 5 minutes:** [JUDGES.md](JUDGES.md)

> **Field result so far:** see the live [/impact]({{LIVE_URL}}/impact) page. It is updated automatically and has a raw CSV.
> A dated snapshot is in [IMPACT-SNAPSHOT.md](IMPACT-SNAPSHOT.md).
>
> **Safety benchmark (held-out scenarios, written before the run):** 12/12 bite messages sent to hospital,
> **0 false "safe"**, 0 under-triage, 4/4 non-snakebite controls correctly kept out. Full table in [BENCHMARK-RESULTS.md](BENCHMARK-RESULTS.md).

Dansh is a free, open-source web app in **Hindi and English** for the moment someone is bitten by a snake in rural India. It does two things:

1. **Bitten now → an emergency agent.** You type or say what happened, the way people actually speak:
   *"papa ko saanp ne kaata, rassi baandh di"* ("a snake bit papa, we tied a rope").
   Dansh replies in seconds:
   - call 108 (and 15400 in the five states where that helpline runs);
   - go to a government hospital that has antivenom, with the nearest ones shown on a map;
   - what to do on the way, and what **never** to do;
   - a correction for what was already done ("a band was already tied: don't tighten it, tell the doctor").

   It asks 4 yes/no danger-sign questions. A "yes" escalates the advice immediately.
2. **3-minute check → behaviour change you can measure.** Six real-life decisions (tourniquet? ojha? cut and suck? wait for symptoms? painless night bite? walk or be carried?), then a short lesson, then six parallel decisions. Every completed check is counted anonymously on a public live page, as the share of people choosing a dangerous action before and after.

## Why this problem (size and severity)

| | Figure | Source |
|---|---|---|
| Deaths | **~58,000 a year** (1.2 M from 2000–2019), about half of all snakebite deaths worldwide; 94% rural, 77% outside hospital | Suraweera et al., *eLife* 2020 (Million Death Study) |
| Lifetime risk | **1 in 250** Indians die of snakebite before age 70 (higher in 8 states holding ~55% of the population) | same |
| Bites | **3–4 million a year** (Health Ministry estimate) | MoHFW at NAP-SE launch, Mar 2024 |
| Newer, lower estimate | An ICMR community survey (60 M people, 25 districts, 11 states; excludes UP and Bihar) recorded 0.33 deaths per 100,000. **43% of deaths happened outside hospital**, and 53% of victims were below the poverty line. | ICMR, *Nature Communications*, 10 Nov 2025 |
| Cost | Out-of-pocket ₹6,500 on average; **₹27,400 in private hospitals** vs ₹3,900 in public ones | same |
| What goes wrong | Tourniquets used in **70%** of cases (coastal Karnataka) and **69–90%** (Tamil Nadu); a traditional healer was the **first contact for 64%** in a tribal block; healer use was linked to higher mortality. Reaching hospital within 30 minutes was associated with better survival. | Manipal VENOMS registry; Ralph et al., *Trans R Soc Trop Med Hyg* 2025 |
| Government goal | Halve snakebite deaths by 2030. Public education and referral are named levers. | NAP-SE, MoHFW, Mar 2024 |

**We use the estimates honestly.** The older verbal-autopsy estimate (~58k/yr) and the newer ICMR survey disagree by an order of magnitude. Every study agrees on the failure Dansh targets: **delay, tourniquets and healers in the first hour.** That failure needs no hospital, no doctor and no new drug to fix, only the right decision made by a relative with a phone.

## How it works (and what the AI is not allowed to do)

```
message (hi/en/hinglish)
   │
   ├─► keyword parser (offline, deterministic) ─┐
   └─► optional LLM reader (2.5 s budget) ──────┤ monotone merge: the model may ADD a danger sign,
                                                 │ never remove one, never move a bite out of protocol
                                                 ▼
                                       facts (snake? danger signs? what was already done? state? child?)
                                                 │
                                                 ▼
                     protocol engine (app/protocol.py), rules R0–R10 from MoHFW STG 2017
                                                 │   safety invariants checked on every answer:
                                                 │   any possible bite ⇒ 108 + hospital + 3 never-dos
                                                 ▼
                     plan: level, ordered steps, never-dos, corrections, follow-up questions, rule trace
```

- **Code decides, nothing is generated.** Every sentence the user sees is a fixed, bilingual item in [`app/content.py`](app/content.py) with its source and page number from the Health Ministry's *Standard Treatment Guidelines: Management of Snake Bite (2017)*. The rule trace is shown under "Why this advice?".
- **Rules only move toward more care.** No input can produce "stay home". Uncertain cases ("something bit me", "maybe a rat", "no bite mark but woke up with drooping eyelids") are treated as snakebite. Denials are honoured only when explicit ("no bleeding"), because in Hindi *"saans nahi aa rahi"* means *can't breathe*.
- **Nearest hospitals** come from OpenStreetMap, looked up in the browser. Government hospitals and CHCs, which keep antivenom, are preferred.

## Proof

- **Tests:** `python3 -m pytest -q tests`. The 80+ tests include a 3,000-message fuzz test, monotonicity over all combinations of facts, every audit-found input as a regression test, and the impact-integrity rules.
- **Scenario benchmark:** `python3 scripts/run_eval.py <url>` and `--cases eval_cases/holdout.yaml`. Expected outcomes are written before each run and never edited afterwards. Misses are kept in [BENCHMARK-RESULTS.md](BENCHMARK-RESULTS.md).
- **Independent audit:** the loop is recorded in [`loop/`](loop/). A fresh auditor scores each round, a separate verifier must run the tests itself, and protected paths stop the loop from "fixing" its own benchmark.

## Impact measurement (and its limits)

- Counterbalanced pre/post: question set A or B comes first at random, so an easier set can't pass for learning.
- Excluded from the public numbers: test traffic (`?test=1`, the eval runner, the developers), more than 5 completions per device per day, and checks finished faster than anyone could read them.
- Nothing personal is stored: no names, phone numbers, message text or raw IPs. A device is identified by a salted hash that rotates daily. State and role are optional and chosen from fixed lists.
- **Limits:** this measures intended behaviour right after the lesson, not months later or in a real emergency, and early users are self-selected through shared links. See [CLAIMS.md](CLAIMS.md).

## Run it

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8000          # http://localhost:8000  (add ?test=1 to not be counted)
python3 -m pytest -q tests
python3 scripts/run_eval.py http://localhost:8000
```

Deploy: `Dockerfile` (any container platform), or [`deploy/cloud-config.yaml`](deploy/cloud-config.yaml) for any Ubuntu VM. That gives HTTPS through Caddy and sslip.io, plus a self-updater. Optional: set `ANTHROPIC_API_KEY` to enable the LLM reader. When enabled, the message text is sent to that provider. Without it, nothing leaves the server.

## Built in AgentFoundry

See [AGENTFOUNDRY.md](AGENTFOUNDRY.md) for how the project was built and tested in the official IDE.

## Not medical advice

Dansh does not diagnose and is not a doctor. It repeats the first-aid steps of the Government of India's guidelines and always sends a possible snakebite to a hospital. It has not been clinically validated in the field.

MIT licence.
