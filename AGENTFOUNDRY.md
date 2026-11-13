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

_To be filled with the commit hashes and screenshots from the steps above._
