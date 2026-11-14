# Submission: copy into the GitHub issue form

**Filed 14 Nov 2026 ~20:00 UTC as https://github.com/karlmehta/code-for-a-billion/issues/143.** The issue can be edited; update the impact section there if real users arrive.

Form: https://github.com/karlmehta/code-for-a-billion/issues/new?template=submission.yml
Title: `[Submission] Dansh: the first 30 minutes after a snakebite (Health)`

---

**Team / Project name**
Dansh (दंश)

**Team members (names + GitHub handles)**
VALOR (@acirema792)

**Problem statement**
Snakebite kills tens of thousands of Indians a year, mostly farm workers and children in villages. Many die at home or on the way, because the first hour is lost to a tight rope, a cut, or a trip to the ojha before the hospital. A government hospital with antivenom treats it free. What's missing is the right decision, in the family's own language, in the first minutes.

**What you built, and how AgentFoundry (AF) was used**
Dansh is a free web app in Hindi and English (it also reads Hinglish).

(1) **Bitten now.** Type or say what happened, e.g. "papa ko saanp ne kaata, rassi baandh di" ("a snake bit papa, we tied a rope"). A deterministic protocol built from the Health Ministry's Standard Treatment Guidelines (2017) replies in under a second (about 0.4 s round trip in our live runs):
- call 108 (and 15400 in its pilot states);
- the nearest government hospitals, from OpenStreetMap;
- what to do on the way and what never to do;
- a correction for what was already done.

It asks 4 danger-sign questions, and a "yes" escalates the advice. Every sentence cites its guideline page. An optional language model may only add danger signs. It never writes advice and never lowers the urgency.

(2) **3-minute check.** Six real decisions (tourniquet, ojha, cut and suck, waiting, painless night bites, walking), then a lesson, then six parallel decisions. The question sets are counterbalanced. Every completed check is counted anonymously on a live public impact page.

AF: The project was opened, installed and tested in AgentFoundry (218 tests passing in AF's terminal); AF's SMART-Code agent wrote a content-integrity test suite, which was run and committed from AF (d172219). Details and screenshots: AGENTFOUNDRY.md.

**GitHub repository URL**
https://github.com/acirema792/dansh

**Demo URL (live app or video)**
https://65-20-73-107.sslip.io (judges: add `?test=1` so your clicks aren't counted; 5-minute walkthrough in JUDGES.md)

**Scale & severity of the problem**
- India has about half of the world's snakebite deaths: ~58,000 a year by the Million Death Study (eLife 2020), and a 1-in-250 risk of dying of snakebite before age 70.
- The Health Ministry estimates 3–4 million bites a year (NAP-SE, Mar 2024).
- A 2025 ICMR community survey recorded lower mortality in its districts (it excludes UP and Bihar). In that survey, 43% of deaths happened outside hospital and about half of victims were below the poverty line.
- Private treatment averages ₹27,400, against ₹3,900 in public hospitals.
- Field studies find tourniquets in 69–90% of cases, and a traditional healer was the first contact for 64% of victims in a Tamil Nadu tribal block.
- The government aims to halve snakebite deaths by 2030.

Sources are linked in the README.

**Deployment & impact data**
Live since 13 Nov 2026 15:50 UTC on Vultr Mumbai, updated from the public repo by a self-updater (the running commit is shown at /api/health).

**Field use, stated plainly:** as of 14 Nov 2026 19:50 UTC, **0 people outside the team** had completed the 3-minute check, and the emergency agent had 0 non-test uses. We do not present test traffic or invented users as impact. The measurement is live and public: it counts each completed check anonymously, excludes test traffic, more than 5 a day per device, more than 150 a day per network, and too-fast completions, and reports the before/after share of people choosing a dangerous action with 95% intervals: https://65-20-73-107.sslip.io/impact (raw CSV linked there). Any numbers that appear there after submission are real users, counted by those rules.

**What we can prove today: safety on messages we did not write.** Seven rounds of independent reviewers wrote fresh, realistic messages (Hinglish, typos, Devanagari, unknown biters, people touching snakes) and ran them against the deployed code before any fix:
- Latest round (round 7, commit 3103d26, the deployed parser): **224 fresh messages, 0 bite messages left without a hospital referral**, 1 clear danger sign graded URGENT instead of CRITICAL, 0 plain bites over-escalated. The previous version, which round 6 rejected, missed 1 of these bite messages, and the earlier live version missed 1 and under-graded 5 danger signs.
- Earlier rounds found 25, 30, 15 and 12 missed bite messages on their fresh sets. Each finding was fixed and added to a regression corpus, now **1,294 labelled messages: 0 false "safe", 0 danger sign under-graded**.
- Scenario benchmarks with expectations written before the first run: **54/54 matched; 42/42 bite cases sent to hospital**.
- Every reply shows 108. Any reply that mentions a snake but isn't read as a bite also says "if you are not sure, treat it as a snakebite and go to the hospital".

Full history, including every miss: BENCHMARK-RESULTS.md and loop/audits/ in the repo.

**Track / category**
Health

**Contact email**
Via GitHub: @acirema792

**Confirmations**
- [x] Built using AgentFoundry (AF), the official IDE (session, commit d172219 and screenshots in AGENTFOUNDRY.md)
- [x] Our repository is public and includes a README with setup steps
- [x] The demo link works and is accessible to judges
