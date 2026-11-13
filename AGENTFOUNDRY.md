# Building and testing Dansh in AgentFoundry

The hackathon requires projects to be built in AgentFoundry (AF), the official IDE.
This file records what was done in AF. It is filled in from the actual session, not from intentions.

## Steps (about 15 minutes)

1. Open AgentFoundry → **Open project** → clone `https://github.com/acirema792/dansh`.
2. In AF's terminal: `pip install -r requirements.txt pytest` and then `python3 -m pytest -q tests`. Expect every test to pass.
3. **Build → Evals:** run the scenario suite from AF's terminal against the live site:
   `python3 scripts/run_eval.py https://65-20-73-107.sslip.io --cases eval_cases/holdout.yaml`.
4. **Build → Tools:** test the protocol engine in isolation with JSON args, e.g. `{"message": "papa ko saanp ne kaata"}` against `POST /api/consult`.
5. Ask SMART-Code for one real improvement (suggested: *"add Marathi and Bengali translations of UI strings in static/app.js"*, or *"add a test that every FOLLOW_UPS flag exists in RED_FLAGS"*). Review it, run the tests, and commit from AF's source-control panel.
6. Push. Take 2–3 screenshots (the project open in AF, the tests passing, the commit) for `docs/af/`.

## What was done in AF

Session on 13 Nov 2026, on the team's Mac, in AgentFoundry (project `dansh`, opened from `~/Documents/dansh`):

| Step | What happened | Evidence |
|---|---|---|
| Project open | Repo checked out at `2458031` inside AF's project folder | [screenshot 1](docs/af/1-project-and-smart-code.png) |
| Full test suite in AF's terminal | `python -m pytest -q tests` → **218 passed in 98.6 s** (Python 3.9.6, the Mac's system Python, in a `.venv`). The first `pip install` failed on Python 3.9 because of a pinned FastAPI version; that pin was relaxed and the fix is commit `2458031`. | AF terminal output |
| Improvement by SMART-Code (Cloud · Smart, Haiku + GPT) | Asked for `tests/test_content_integrity.py`: every follow-up question maps to a red flag, every advice item has English and Hindi text and a source in `SOURCES`, every quiz concept's lesson exists, every Hindi string contains Devanagari. SMART-Code read `app/content.py`, `app/quiz.py` and `tests/test_integrity.py`, then wrote the file; each tool call was approved by hand. | [screenshot 1](docs/af/1-project-and-smart-code.png) |
| Test the new code in AF | `pytest tests/test_content_integrity.py` → **4 passed** | [screenshot 2](docs/af/2-new-test-passes-in-af.png) |
| Commit and push from AF | Commit **`d172219`** pushed to `main` from AF's terminal | [screenshot 3](docs/af/3-commit-and-push-from-af.png) |

The rest of the code was written outside AF and is in the same public repo; AF was used to build, run and test it and to add the commit above. We say so plainly rather than claim more.
