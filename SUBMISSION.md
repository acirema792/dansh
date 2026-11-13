# Submission: copy into the GitHub issue form

Form: https://github.com/karlmehta/code-for-a-billion/issues/new?template=submission.yml
Title: `[Submission] Dansh: the first 30 minutes after a snakebite (Health)`

---

**Team / Project name**
Dansh (दंश)

**Team members (names + GitHub handles)**
{{NAME}} (@acirema792)

**Problem statement**
Snakebite kills tens of thousands of Indians a year, mostly farm workers and children in villages. Many die at home or on the way, because the first hour is lost to a tight rope, a cut, or a trip to the ojha before the hospital. A government hospital with antivenom treats it free. What's missing is the right decision, in the family's own language, in the first minutes.

**What you built, and how AgentFoundry (AF) was used**
Dansh is a free web app in Hindi and English (it also reads Hinglish).

(1) **Bitten now.** Type or say what happened, e.g. "papa ko saanp ne kaata, rassi baandh di" ("a snake bit papa, we tied a rope"). A deterministic protocol built from the Health Ministry's Standard Treatment Guidelines (2017) replies in under a second:
- call 108 (and 15400 in its pilot states);
- the nearest government hospitals, from OpenStreetMap;
- what to do on the way and what never to do;
- a correction for what was already done.

It asks 4 danger-sign questions, and a "yes" escalates the advice. Every sentence cites its guideline page. An optional language model may only add danger signs. It never writes advice and never lowers the urgency.

(2) **3-minute check.** Six real decisions (tourniquet, ojha, cut and suck, waiting, painless night bites, walking), then a lesson, then six parallel decisions. The question sets are counterbalanced. Every completed check is counted anonymously on a live public impact page.

AF: {{AF_SENTENCE}}

**GitHub repository URL**
https://github.com/acirema792/dansh

**Demo URL (live app or video)**
https://65-20-73-107.sslip.io (judges: add `?test=1` so your clicks aren't counted; 5-minute walkthrough in JUDGES.md)

**Scale & severity of the problem**
- India has about half of the world's snakebite deaths: ~58,000 a year by the Million Death Study (eLife 2020), and a 1-in-250 risk of dying of snakebite before age 70.
- The Health Ministry estimates 3–4 million bites a year (NAP-SE, Mar 2024).
- A 2025 ICMR community survey recorded lower mortality in its districts (it excludes UP and Bihar). In that survey, 43% of deaths happened outside hospital and 53% of victims were below the poverty line.
- Private treatment averages ₹27,400, against ₹3,900 in public hospitals.
- Field studies find tourniquets in 69–90% of cases, and a traditional healer was the first contact for 64% of victims in a Tamil Nadu tribal block.
- The government aims to halve snakebite deaths by 2030.

Sources are linked in the README.

**Deployment & impact data**
Live since 13 Nov 2026 15:50 UTC on Vultr Mumbai. As of {{SNAPSHOT_TIME}}:
- **{{N}} people** completed the check, on {{DEVICES}} devices;
- **{{DANGER_PRE}}% chose at least one dangerous action before the lesson, {{DANGER_POST}}% after**;
- average score {{PRE}}% → {{POST}}%.

Per-decision results, the raw CSV and the exclusion rules (test traffic, more than 5 a day per device, too-fast completions) are at https://65-20-73-107.sslip.io/impact. Limits: this measures decisions right after the lesson, among self-selected users, not outcomes.

Safety benchmark on held-out scenarios written before their first run: 12/12 bite messages sent to hospital, 0 false "safe".

**Track / category**
Health

**Contact email**
{{EMAIL}}

**Confirmations**
- [ ] Built using AgentFoundry (AF), the official IDE ← tick only after the AF session in AGENTFOUNDRY.md is done
- [x] Our repository is public and includes a README with setup steps
- [x] The demo link works and is accessible to judges
