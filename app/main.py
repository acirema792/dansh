"""Dansh web app: emergency agent, 3-minute check, live impact page."""
from __future__ import annotations

import csv
import io
import json
import os
import random
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import llm, quiz, store
from .content import SOURCES, cite, text
from .parser import parse
from .protocol import check_invariants, decide

VERSION = "1.0.0"
STATIC = Path(__file__).resolve().parent.parent / "static"
TEST_TOKEN = os.environ.get("DANSH_TEST_TOKEN", "")
MAX_COMPLETIONS_PER_DEVICE_PER_DAY = int(os.environ.get("DANSH_MAX_PER_DEVICE", "5"))

app = FastAPI(title="Dansh", version=VERSION, docs_url="/api/docs", redoc_url=None)
store.init()


@app.middleware("http")
async def headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("Cache-Control", "no-cache")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "geolocation=(self), microphone=(self)"
    return resp


def _ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return (fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "")) or ""


def _is_test(request: Request) -> bool:
    """Test traffic is excluded from the impact numbers.

    Anyone can opt out of being counted with ?test=1 or the header; the eval runner
    always does. A configured DANSH_TEST_TOKEN is also accepted.
    """
    if request.query_params.get("test") == "1":
        return True
    h = request.headers.get("x-dansh-test", "")
    return bool(h) and (h == "1" or (TEST_TOKEN and h == TEST_TOKEN))


# ----------------------------------------------------------------------------- emergency agent
class ConsultIn(BaseModel):
    message: str = Field(..., max_length=2000)
    lang: str | None = Field(None, pattern="^(en|hi)$")
    answered: dict[str, bool] = Field(default_factory=dict)
    state: str | None = Field(None, max_length=40)


@app.post("/api/consult")
def consult(body: ConsultIn, request: Request):
    t0 = time.time()
    facts = parse(body.message)
    if body.state and not facts.state:
        facts.state = body.state.strip().lower()
    parser_used = "keywords"
    added: list[str] = []
    meta: dict = {}
    if llm.enabled() and body.message.strip():
        extra, meta = llm.read(body.message)
        facts, added = llm.merge(facts, extra)
        parser_used = "keywords+llm" if meta.get("ok") else "keywords (llm unavailable)"
    plan = decide(facts, lang=body.lang, answered=body.answered)
    errs = check_invariants(plan)
    if errs:  # should be impossible; fail safe rather than show a broken plan
        raise HTTPException(500, f"safety invariant failed: {errs}")
    ms = int((time.time() - t0) * 1000)
    store.log_consult(plan.lang, plan.level, sorted(set(facts.red_flags) | {k for k, v in body.answered.items() if v}),
                      parser_used, ms, store.device_hash(_ip(request)), _is_test(request))
    out = plan.to_dict()
    out["facts"] = facts.to_dict()
    out["parser"] = {"used": parser_used, "llm_added": added, "llm_model": meta.get("model"), "ms": ms}
    return out


# ----------------------------------------------------------------------------- 3-minute check
class StartIn(BaseModel):
    lang: str = Field("en", pattern="^(en|hi)$")
    src: str | None = Field(None, max_length=24)


@app.post("/api/learn/start")
def learn_start(body: StartIn, request: Request):
    sid = secrets.token_urlsafe(12)
    pre, post = quiz.assign_forms()
    store.new_session(sid, body.lang, pre, post, body.src, store.device_hash(_ip(request)), _is_test(request))
    return {"session": sid, "questions": quiz.questions(pre, body.lang, random.Random(sid)), "form": pre}


class AnswersIn(BaseModel):
    session: str
    answers: dict[str, str]


def _lesson(lang: str, wrong: list[str]) -> list[dict]:
    cards = []
    for c in quiz.ORDER:
        item = quiz.CONCEPTS[c]["lesson"]
        cards.append({"concept": c, "title": quiz.CONCEPTS[c][lang], "text": text(item, lang), "source": cite(item),
                      "missed": c in wrong})
    cards.sort(key=lambda x: not x["missed"])  # missed concepts first
    return cards


@app.post("/api/learn/pre")
def learn_pre(body: AnswersIn):
    s = store.get_session(body.session)
    if not s:
        raise HTTPException(404, "unknown session")
    if s["pre_answers"]:
        raise HTTPException(409, "already answered")
    scored = quiz.score(s["pre_form"], body.answers)
    if scored["answered"] < scored["total"]:
        raise HTTPException(422, "answer every question")
    store.save_pre(body.session, body.answers, scored)
    wrong = [c for c, v in scored["per_concept"].items() if not v["correct"]]
    lang = s["lang"]
    return {"pre": {"correct": scored["correct"], "total": scored["total"], "dangerous": scored["dangerous"]},
            "lesson": _lesson(lang, wrong),
            "questions": quiz.questions(s["post_form"], lang, random.Random(body.session + "post")),
            "form": s["post_form"]}


class PostIn(AnswersIn):
    state: str | None = Field(None, max_length=40)
    role: str | None = Field(None, max_length=24)


@app.post("/api/learn/post")
def learn_post(body: PostIn, request: Request):
    s = store.get_session(body.session)
    if not s:
        raise HTTPException(404, "unknown session")
    if not s["pre_answers"]:
        raise HTTPException(409, "pre-test first")
    if s["completed_at"]:
        raise HTTPException(409, "already completed")
    scored = quiz.score(s["post_form"], body.answers)
    if scored["answered"] < scored["total"]:
        raise HTTPException(422, "answer every question")
    pre = quiz.score(s["pre_form"], json.loads(s["pre_answers"]))
    per = {c: {"pre": pre["per_concept"][c]["correct"], "post": scored["per_concept"][c]["correct"],
               "pre_danger": pre["per_concept"][c]["dangerous"], "post_danger": scored["per_concept"][c]["dangerous"]}
           for c in quiz.ORDER}
    # Anti-stuffing: past a few completions per device per day, keep the row but mark it test.
    over = store.device_completions_today(s["device"]) >= MAX_COMPLETIONS_PER_DEVICE_PER_DAY
    store.save_post(body.session, body.answers, scored, per, body.state, body.role)
    if over and not s["is_test"]:
        store.mark_test(body.session)
    review = []
    for c in quiz.ORDER:
        if not scored["per_concept"][c]["correct"]:
            item = quiz.CONCEPTS[c]["lesson"]
            review.append({"concept": c, "title": quiz.CONCEPTS[c][s["lang"]], "text": text(item, s["lang"])})
    return {"pre": {"correct": pre["correct"], "dangerous": pre["dangerous"]},
            "post": {"correct": scored["correct"], "dangerous": scored["dangerous"]},
            "total": scored["total"], "review": review}


class ShareIn(BaseModel):
    session: str


@app.post("/api/learn/shared")
def learn_shared(body: ShareIn):
    store.mark_shared(body.session)
    return {"ok": True}


# ----------------------------------------------------------------------------- impact
def _pct(n: int, d: int) -> float | None:
    return round(100.0 * n / d, 1) if d else None


def impact_summary(include_test: bool = False) -> dict:
    rows = store.completed_sessions(include_test)
    n = len(rows)
    per = {c: {"pre": 0, "post": 0, "pre_danger": 0, "post_danger": 0} for c in quiz.ORDER}
    any_danger_pre = any_danger_post = 0
    pre_total = post_total = 0
    improved = same = worse = 0
    by_lang: dict[str, int] = {}
    by_state: dict[str, int] = {}
    by_role: dict[str, int] = {}
    by_form = {"A->B": 0, "B->A": 0}
    shared = 0
    first = last = None
    for r in rows:
        pc = json.loads(r["per_concept"])
        for c in quiz.ORDER:
            for k in per[c]:
                per[c][k] += int(bool(pc[c][k]))
        any_danger_pre += int(r["pre_dangerous"] > 0)
        any_danger_post += int(r["post_dangerous"] > 0)
        pre_total += r["pre_correct"]
        post_total += r["post_correct"]
        d = r["post_correct"] - r["pre_correct"]
        improved += d > 0
        same += d == 0
        worse += d < 0
        by_lang[r["lang"]] = by_lang.get(r["lang"], 0) + 1
        if r["state"]:
            by_state[r["state"]] = by_state.get(r["state"], 0) + 1
        if r["role"]:
            by_role[r["role"]] = by_role.get(r["role"], 0) + 1
        by_form[f"{r['pre_form']}->{r['post_form']}"] += 1
        shared += r["shared"]
        first = first or r["completed_at"]
        last = r["completed_at"]
    k = len(quiz.ORDER)
    consults = store.consult_rows(include_test)
    levels: dict[str, int] = {}
    for c in consults:
        levels[c["level"]] = levels.get(c["level"], 0) + 1
    return {
        "generated_at": time.time(),
        "includes_test_traffic": include_test,
        "learn": {
            "started": store.started_count(include_test),
            "completed": n,
            "unique_devices": len({r["device"] for r in rows}),
            "mean_score_pre_pct": _pct(pre_total, n * k),
            "mean_score_post_pct": _pct(post_total, n * k),
            "chose_dangerous_action_pre_pct": _pct(any_danger_pre, n),
            "chose_dangerous_action_post_pct": _pct(any_danger_post, n),
            "improved": improved, "same": same, "worse": worse,
            "per_concept": {c: {"label_en": quiz.CONCEPTS[c]["en"], "label_hi": quiz.CONCEPTS[c]["hi"],
                                "correct_pre_pct": _pct(per[c]["pre"], n), "correct_post_pct": _pct(per[c]["post"], n),
                                "dangerous_pre_pct": _pct(per[c]["pre_danger"], n),
                                "dangerous_post_pct": _pct(per[c]["post_danger"], n)} for c in quiz.ORDER},
            "by_lang": by_lang, "by_state": by_state, "by_role": by_role, "by_form_order": by_form,
            "shared": shared, "first_completed_at": first, "last_completed_at": last,
        },
        "consults": {"total": len(consults), "by_level": levels,
                     "note": "Emergency-agent uses. These include people trying the tool out; they are not counted as emergencies."},
    }


@app.get("/api/impact")
def impact():
    return impact_summary(False)


@app.get("/api/impact/sessions.csv")
def impact_csv():
    rows = store.completed_sessions(False)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["completed_utc", "lang", "pre_form", "post_form", "pre_correct", "post_correct", "pre_dangerous",
                "post_dangerous", "state", "role", "src"])
    for r in rows:
        w.writerow([time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(r["completed_at"])), r["lang"], r["pre_form"],
                    r["post_form"], r["pre_correct"], r["post_correct"], r["pre_dangerous"], r["post_dangerous"],
                    r["state"] or "", r["role"] or "", r["src"] or ""])
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")


# ----------------------------------------------------------------------------- misc
@app.get("/api/health")
def health():
    return {"ok": True, "version": VERSION, "llm": llm.enabled(), "llm_model_config": llm.MODEL if llm.enabled() else None}


@app.get("/api/sources")
def sources():
    return SOURCES


@app.get("/impact")
def impact_page():
    return FileResponse(STATIC / "impact.html")


@app.get("/check")
def check_page():
    return FileResponse(STATIC / "index.html")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/robots.txt")
def robots():
    return Response("User-agent: *\nAllow: /\n", media_type="text/plain")


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.exception_handler(HTTPException)
async def http_err(_: Request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
