"""Audit round 1: impact-integrity and abuse findings F4-F7, F12."""
import os
import tempfile

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "i.db"))
os.environ.setdefault("DANSH_RATE_PER_MIN", "100000")

from fastapi.testclient import TestClient  # noqa: E402

from app import main, quiz  # noqa: E402


def _run(c, headers=None, state=None, role=None, src=None):
    h = headers or {}
    r = c.post("/api/learn/start", json={"lang": "en", "src": src}, headers=h).json()
    ans = {q["concept"]: quiz.correct_option(q["concept"], r["form"]) for q in r["questions"]}
    r2 = c.post("/api/learn/pre", json={"session": r["session"], "answers": ans}, headers=h).json()
    ans2 = {q["concept"]: quiz.correct_option(q["concept"], r2["form"]) for q in r2["questions"]}
    return c.post("/api/learn/post", json={"session": r["session"], "answers": ans2, "state": state, "role": role},
                  headers=h)


def test_f4_forged_xff_does_not_bypass_device_cap(monkeypatch):
    monkeypatch.setattr(main, "MIN_PRE_SECS", 0)
    monkeypatch.setattr(main, "MIN_POST_SECS", 0)
    c = TestClient(main.app, client=("10.7.7.7", 1))
    before = c.get("/api/impact").json()["learn"]["completed"]
    for i in range(8):
        _run(c, headers={"x-forwarded-for": f"1.2.3.{i}"})
    assert c.get("/api/impact").json()["learn"]["completed"] - before == main.MAX_COMPLETIONS_PER_DEVICE_PER_DAY


def test_f5_too_fast_is_excluded(monkeypatch):
    monkeypatch.setattr(main, "MIN_PRE_SECS", 20)
    monkeypatch.setattr(main, "MIN_POST_SECS", 30)
    c = TestClient(main.app, client=("10.8.8.8", 1))
    before = c.get("/api/impact").json()["learn"]
    assert _run(c).status_code == 200
    after = c.get("/api/impact").json()["learn"]
    assert after["completed"] == before["completed"]
    assert after["excluded"].get("too_fast", 0) == before["excluded"].get("too_fast", 0) + 1


def test_f6_free_text_not_published(monkeypatch):
    monkeypatch.setattr(main, "MIN_PRE_SECS", 0)
    monkeypatch.setattr(main, "MIN_POST_SECS", 0)
    c = TestClient(main.app, client=("10.6.6.6", 1))
    _run(c, state="=HYPERLINK(\"x\")", role="<script>", src="=cmd|evil")
    imp = c.get("/api/impact").json()["learn"]
    assert "=HYPERLINK(\"x\")" not in imp["by_state"] and "<script>" not in imp["by_role"]
    assert "=cmd" not in c.get("/api/impact/sessions.csv").text


def test_f7_big_bodies_rejected_and_answers_trimmed():
    c = TestClient(main.app, client=("10.5.5.5", 1))
    big = {"session": "x", "answers": {str(i): "a" * 100 for i in range(500)}}
    assert c.post("/api/learn/pre", json=big).status_code == 413
    r = c.post("/api/consult", json={"message": "snake bit me", "answered": {"x" * 30: True}, "repeat": True})
    assert r.status_code == 200


def test_f7_rate_limit(monkeypatch):
    monkeypatch.setattr(main, "RATE", 3.0)
    main._buckets.clear()
    c = TestClient(main.app, client=("10.4.4.4", 1))
    codes = [c.post("/api/consult", json={"message": "hello"}).status_code for _ in range(6)]
    assert 429 in codes
    main._buckets.clear()


def test_f12_security_headers():
    r = TestClient(main.app).get("/")
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-frame-options"] == "DENY"
