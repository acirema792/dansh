"""Dansh web app: emergency agent, 3-minute check, live impact page."""
from __future__ import annotations

import csv
import io
import json
import os
import random
import re
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import llm, quiz, store
from .content import RED_FLAGS, SOURCES, cite, text
from .parser import parse
from .protocol import check_invariants, decide

VERSION = "1.0.0"
STATIC = Path(__file__).resolve().parent.parent / "static"
TEST_TOKEN = os.environ.get("DANSH_TEST_TOKEN", "")
MAX_COMPLETIONS_PER_DEVICE_PER_DAY = int(os.environ.get("DANSH_MAX_PER_DEVICE", "5"))
MIN_PRE_SECS = float(os.environ.get("DANSH_MIN_PRE_SECS", "20"))
MIN_POST_SECS = float(os.environ.get("DANSH_MIN_POST_SECS", "30"))
SRC_RE = re.compile(r"^[a-z0-9_-]{0,24}$")
ALLOWED_ROLES = {"farmer", "student", "health_worker", "teacher", "parent", "other"}
ALLOWED_STATES = {"Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat",
                  "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh",
                  "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha",
                  "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
                  "Uttar Pradesh", "Uttarakhand", "West Bengal", "Other UT", "Outside India"}

app = FastAPI(title="Dansh", version=VERSION, docs_url="/api/docs", redoc_url=None)
store.init()


MAX_BODY = 16 * 1024
_buckets: dict[str, list[float]] = {}
RATE = float(os.environ.get("DANSH_RATE_PER_MIN", "40"))


def _allow(ip: str) -> bool:
    now = time.time()
    tokens, last = _buckets.get(ip, [RATE, now])
    tokens = min(RATE, tokens + (now - last) * RATE / 60.0)
    if tokens < 1:
        _buckets[ip] = [tokens, now]
        return False
    _buckets[ip] = [tokens - 1, now]
    if len(_buckets) > 50000:
        _buckets.clear()
    return True


CSP = ("default-src 'self'; connect-src 'self' https://overpass-api.de; img-src 'self' data:; "
       "style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


@app.middleware("http")
async def headers(request: Request, call_next):
    if request.method == "POST":
        if "chunked" in request.headers.get("transfer-encoding", "").lower():
            return JSONResponse({"error": "content-length required"}, status_code=411)
        try:
            if int(request.headers.get("content-length") or 0) > MAX_BODY:
                return JSONResponse({"error": "request too large"}, status_code=413)
        except ValueError:
            return JSONResponse({"error": "bad content-length"}, status_code=400)
        allowed = _allow(_ip(request))
        if request.url.path == "/api/consult":
            # Never refuse an emergency answer. Over the limit we still answer (the rules are cheap),
            # but skip the language model and do not log the request.
            request.state.over_limit = not allowed
        elif not allowed:
            return JSONResponse({"error": "too many requests, wait a minute"}, status_code=429)
    resp = await call_next(request)
    resp.headers["Content-Security-Policy"] = CSP
    resp.headers["Strict-Transport-Security"] = "max-age=31536000"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers.setdefault("Cache-Control", "no-cache")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "geolocation=(self), microphone=(self)"
    return resp


def _ip(request: Request) -> str:
    """The client as resolved by uvicorn. X-Forwarded-For is only honoured by uvicorn itself
    (--proxy-headers) when it comes from FORWARDED_ALLOW_IPS, so a client cannot forge it."""
    return request.client.host if request.client else ""


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
    repeat: bool = False  # same message re-rendered (language switch / follow-up): not logged again
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
    over_limit = getattr(request.state, "over_limit", False)
    if llm.enabled() and body.message.strip() and not over_limit:
        extra, meta = llm.read(body.message)
        facts, added = llm.merge(facts, extra)
        parser_used = "keywords+llm" if meta.get("ok") else "keywords (llm unavailable)"
    plan = decide(facts, lang=body.lang, answered={k: v for k, v in body.answered.items() if k in RED_FLAGS})
    errs = check_invariants(plan)
    if errs:  # should be impossible; fail safe rather than show a broken plan
        raise HTTPException(500, f"safety invariant failed: {errs}")
    ms = int((time.time() - t0) * 1000)
    answered_flags = {k for k, v in body.answered.items() if v and k in RED_FLAGS}
    if not body.repeat and not over_limit:
        store.log_consult(plan.lang, plan.level, sorted(set(facts.red_flags) | answered_flags),
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
    src = (body.src or "").lower()
    src = src if SRC_RE.match(src) else "other"
    store.new_session(sid, body.lang, pre, post, src, store.device_hash(_ip(request)), _is_test(request))
    return {"session": sid, "questions": quiz.questions(pre, body.lang, random.Random(sid)), "form": pre}


class AnswersIn(BaseModel):
    session: str = Field(..., max_length=40)
    answers: dict[str, str]

    def clean(self) -> dict[str, str]:
        return {c: str(self.answers.get(c, ""))[:1] for c in quiz.ORDER if c in self.answers}


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
    answers = body.clean()
    scored = quiz.score(s["pre_form"], answers)
    if scored["answered"] < scored["total"]:
        raise HTTPException(422, "answer every question")
    store.save_pre(body.session, answers, scored)
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
    answers = body.clean()
    scored = quiz.score(s["post_form"], answers)
    if scored["answered"] < scored["total"]:
        raise HTTPException(422, "answer every question")
    pre = quiz.score(s["pre_form"], json.loads(s["pre_answers"]))
    per = {c: {"pre": pre["per_concept"][c]["correct"], "post": scored["per_concept"][c]["correct"],
               "pre_danger": pre["per_concept"][c]["dangerous"], "post_danger": scored["per_concept"][c]["dangerous"]}
           for c in quiz.ORDER}
    # Anti-stuffing: past a few completions per device per day, keep the row but mark it test.
    over = store.device_completions_today(s["device"]) >= MAX_COMPLETIONS_PER_DEVICE_PER_DAY
    state = body.state if body.state in ALLOWED_STATES else None
    role = body.role if body.role in ALLOWED_ROLES else None
    store.save_post(body.session, answers, scored, per, state, role)
    # F5 plausibility: nobody reads 6 scenarios in under 20 s, or a lesson + 6 more in under 30 s.
    pre_secs = (s["pre_at"] or 0) - s["created_at"]
    post_secs = time.time() - (s["pre_at"] or time.time())
    reason = None
    if over:
        reason = "device_cap"
    elif pre_secs < MIN_PRE_SECS or post_secs < MIN_POST_SECS:
        reason = "too_fast"
    if reason and not s["is_test"]:
        store.exclude(body.session, reason)
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
            "excluded": store.excluded_counts(),
            "exclusion_rules": {"device_cap_per_day": MAX_COMPLETIONS_PER_DEVICE_PER_DAY,
                                "min_seconds_part1": MIN_PRE_SECS, "min_seconds_lesson_and_part3": MIN_POST_SECS},
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
    def safe(v):
        v = "" if v is None else str(v)
        return "'" + v if v[:1] in ("=", "+", "-", "@") else v

    for r in rows:
        w.writerow([safe(x) for x in [time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(r["completed_at"])), r["lang"], r["pre_form"],
                    r["post_form"], r["pre_correct"], r["post_correct"], r["pre_dangerous"], r["post_dangerous"],
                    r["state"] or "", r["role"] or "", r["src"] or ""]])
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


@app.api_route("/", methods=["GET", "HEAD"])
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/robots.txt")
def robots():
    return Response("User-agent: *\nAllow: /\n", media_type="text/plain")


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.exception_handler(HTTPException)
async def http_err(_: Request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
