Run against `http://localhost:8077` at 2026-11-13T02:32:42+00:00 (app 1.0.0, LLM reader: off, keyword parser only).

- **19/22** cases matched the expected outcome exactly
- **18/18** bite cases sent to hospital (**0 false safe**)
- under-triage (lower level than expected): **0** · over-triage: 1
- controls correctly kept out of the snakebite protocol: **4/4**
- median response time: 4 ms

| # | case | lang | expected | got | result | notes |
|---|---|---|---|---|---|---|
| 1 | `en-basic` | en | URGENT | URGENT | ✅ |  |
| 2 | `hinglish-tourniquet` | hinglish | URGENT | URGENT | ✅ |  |
| 3 | `hi-ptosis` | hi | CRITICAL | CRITICAL | ✅ |  |
| 4 | `hinglish-breathing` | hinglish | CRITICAL | CRITICAL | ✅ |  |
| 5 | `en-krait-occult-bitemark` | en | CRITICAL | CRITICAL | ❌ | missing suspect_krait |
| 6 | `hi-krait-occult` | hi | CRITICAL | CRITICAL | ✅ |  |
| 7 | `en-unknown-bite` | en | POSSIBLE | POSSIBLE | ✅ |  |
| 8 | `en-healer` | en | URGENT | URGENT | ✅ |  |
| 9 | `hinglish-cut-suck` | hinglish | URGENT | CRITICAL | ❌ | level CRITICAL != URGENT |
| 10 | `en-assam-pregnant` | en | URGENT | URGENT | ✅ |  |
| 11 | `en-bleeding` | en | CRITICAL | CRITICAL | ✅ |  |
| 12 | `en-wants-to-stay-home` | en | URGENT | URGENT | ✅ |  |
| 13 | `en-child-bangles` | en | URGENT | URGENT | ❌ | missing child_note |
| 14 | `en-late-weak` | en | CRITICAL | CRITICAL | ✅ |  |
| 15 | `hi-unconscious` | hi | CRITICAL | CRITICAL | ✅ |  |
| 16 | `en-negations` | en | URGENT | URGENT | ✅ |  |
| 17 | `hinglish-cant-breathe` | hinglish | CRITICAL | CRITICAL | ✅ |  |
| 18 | `en-self-harm-and-bite` | en | SUPPORT | SUPPORT | ✅ |  |
| 19 | `ctl-dog` | en | OTHER | OTHER | ✅ |  |
| 20 | `ctl-scorpion` | hinglish | OTHER | OTHER | ✅ |  |
| 21 | `ctl-prevention` | en | INFO | INFO | ✅ |  |
| 22 | `ctl-hello` | en | OFF_TOPIC | OFF_TOPIC | ✅ |  |
