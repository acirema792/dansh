# Judging criteria → evidence

| Criterion (25% each) | What we do | Where to look |
|---|---|---|
| **Size of the problem** | 3–4 M bites a year (MoHFW 2024); India has about half of the world's snakebite deaths; 1-in-250 lifetime risk; most victims are rural farm workers and children. Both the older and the newer, lower mortality estimates are shown. | README "Why this problem" |
| **Severity** | Deaths (~58k/yr by verbal autopsy; ICMR 2025 lower), 43–77% die outside hospital, 53% of victims below the poverty line, ₹27,400 average private treatment cost, tourniquets in 69–90% of cases in field studies | README table; sources linked |
| **Quality of the solution** | Targets the exact failure every study names (delay, tourniquet, healer). Deterministic, cited protocol; monotone safety; Hindi/English/Hinglish; corrects what was already done; danger-sign follow-ups; nearest government hospital; works on low-end phones, no install. | JUDGES.md walkthrough; `app/protocol.py`; BENCHMARK-RESULTS.md; tests |
| **Proven impact** | Live, public, anonymous before/after measurement of dangerous choices among real users, counterbalanced, with abuse exclusions and raw CSV | `/impact`; IMPACT-SNAPSHOT.md |

## Eligibility

| Requirement | Status |
|---|---|
| Built in AgentFoundry | See AGENTFOUNDRY.md |
| Public GitHub repo with README | https://github.com/acirema792/dansh |
| Open source (MIT) | LICENSE |
| Deployed to a cloud | https://65-20-73-107.sslip.io |
| Demo link | https://65-20-73-107.sslip.io |
