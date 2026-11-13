Run against `http://localhost:8077` at 2026-11-13T02:33:25+00:00 (app 1.0.0, LLM reader: off, keyword parser only).

- **15/16** cases matched the expected outcome exactly
- **12/12** bite cases sent to hospital (**0 false safe**)
- under-triage (lower level than expected): **0** · over-triage: 0
- controls correctly kept out of the snakebite protocol: **4/4**
- median response time: 4 ms

| # | case | lang | expected | got | result | notes |
|---|---|---|---|---|---|---|
| 1 | `h-en-russell` | en | URGENT | URGENT | ✅ |  |
| 2 | `h-hinglish-krait-night` | hinglish | CRITICAL | CRITICAL | ✅ |  |
| 3 | `h-hi-ojha-tourniquet` | hi | URGENT | URGENT | ✅ |  |
| 4 | `h-en-walked` | en | URGENT | URGENT | ✅ |  |
| 5 | `h-en-alcohol` | en | URGENT | URGENT | ✅ |  |
| 6 | `h-hinglish-swallow` | hinglish | CRITICAL | CRITICAL | ✅ |  |
| 7 | `h-en-vomit-blood` | en | CRITICAL | CRITICAL | ❌ | missing late_note |
| 8 | `h-hi-child` | hi | URGENT | URGENT | ✅ |  |
| 9 | `h-en-mp-helpline` | en | URGENT | URGENT | ✅ |  |
| 10 | `h-en-dont-know-snake` | en | URGENT | URGENT | ✅ |  |
| 11 | `h-hinglish-killed-snake` | hinglish | URGENT | URGENT | ✅ |  |
| 12 | `h-en-not-responding` | en | CRITICAL | CRITICAL | ✅ |  |
| 13 | `h-ctl-bee` | en | OTHER | OTHER | ✅ |  |
| 14 | `h-ctl-monkey` | hinglish | OTHER | OTHER | ✅ |  |
| 15 | `h-ctl-sleep-advice` | en | INFO | INFO | ✅ |  |
| 16 | `h-ctl-fever` | en | OFF_TOPIC | OFF_TOPIC | ✅ |  |
