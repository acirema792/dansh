Run against `https://65-20-73-107.sslip.io` at 2026-11-13T16:08:22+00:00 (app 1.0.0, LLM reader: off, keyword parser only).

- **14/16** cases matched the expected outcome exactly
- **12/12** bite cases sent to hospital (**0 false safe**)
- under-triage (lower level than expected): **1** · over-triage: 0
- controls correctly kept out of the snakebite protocol: **3/4**
- median response time: 485 ms

| # | case | lang | expected | got | result | notes |
|---|---|---|---|---|---|---|
| 1 | `h2-en-farmer-ankle` | en | URGENT | URGENT | ✅ |  |
| 2 | `h2-hinglish-viper-swelling` | hinglish | URGENT | URGENT | ✅ |  |
| 3 | `h2-hi-gums` | hi | CRITICAL | CRITICAL | ✅ |  |
| 4 | `h2-en-turmeric` | en | URGENT | URGENT | ✅ |  |
| 5 | `h2-hinglish-krait-morning` | hinglish | CRITICAL | CRITICAL | ✅ |  |
| 6 | `h2-en-double-vision` | en | CRITICAL | URGENT | ❌ | level URGENT != CRITICAL |
| 7 | `h2-en-temple` | en | URGENT | URGENT | ✅ |  |
| 8 | `h2-hi-pregnant` | hi | URGENT | URGENT | ✅ |  |
| 9 | `h2-en-no-symptoms-wait` | en | URGENT | URGENT | ✅ |  |
| 10 | `h2-hinglish-chubha-dark` | hinglish | POSSIBLE | POSSIBLE | ✅ |  |
| 11 | `h2-en-breath-worse` | en | CRITICAL | CRITICAL | ✅ |  |
| 12 | `h2-en-delhi` | en | URGENT | URGENT | ✅ |  |
| 13 | `h2-ctl-snake-in-house` | en | INFO | URGENT | ❌ | level URGENT != INFO; should not include go_hospital; false alarm: control triggered the snakebite protocol |
| 14 | `h2-ctl-dog-hinglish` | hinglish | OTHER | OTHER | ✅ |  |
| 15 | `h2-ctl-scorpion-en` | en | OTHER | OTHER | ✅ |  |
| 16 | `h2-ctl-headache` | en | OFF_TOPIC | OFF_TOPIC | ✅ |  |
