"""SQLite storage. No names, phone numbers, free text or raw IPs are stored.

Emergency consults keep only the parsed flags and the plan level, never the message.
Learning sessions keep answers, language and the optional self-reported state/role.
Device counts use a salted hash of the IP that is rotated daily, so a device cannot
be followed across days.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timezone

DB_PATH = os.environ.get("DANSH_DB", os.path.join(os.path.dirname(__file__), "..", "data", "dansh.db"))
_lock = threading.Lock()
def _load_salt() -> str:
    if os.environ.get("DANSH_SALT"):
        return os.environ["DANSH_SALT"]
    path = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), "salt")
    try:
        with open(path) as fh:
            return fh.read().strip()
    except OSError:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        salt = secrets.token_hex(16)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write(salt)
        return salt


_SALT = _load_salt()

SCHEMA = """
CREATE TABLE IF NOT EXISTS learn_sessions (
  id TEXT PRIMARY KEY,
  created_at REAL NOT NULL,
  completed_at REAL,
  lang TEXT, pre_form TEXT, post_form TEXT,
  pre_answers TEXT, post_answers TEXT,
  pre_correct INTEGER, post_correct INTEGER,
  pre_dangerous INTEGER, post_dangerous INTEGER,
  per_concept TEXT,
  state TEXT, role TEXT, src TEXT,
  device TEXT, is_test INTEGER NOT NULL DEFAULT 0,
  shared INTEGER NOT NULL DEFAULT 0,
  pre_at REAL, excluded TEXT, network TEXT
);
CREATE TABLE IF NOT EXISTS consults (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at REAL NOT NULL,
  lang TEXT, level TEXT, flags TEXT, parser TEXT, latency_ms INTEGER,
  device TEXT, is_test INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_learn_done ON learn_sessions(completed_at, is_test);
"""


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def init() -> None:
    with _lock, _conn() as c:
        c.executescript(SCHEMA)
        cols = {r[1] for r in c.execute("PRAGMA table_info(learn_sessions)")}
        for col, typ in (("pre_at", "REAL"), ("excluded", "TEXT"), ("network", "TEXT")):
            if col not in cols:
                c.execute(f"ALTER TABLE learn_sessions ADD COLUMN {col} {typ}")


def device_hash(ip: str | None) -> str:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return hashlib.sha256(f"{_SALT}|{day}|{ip or ''}".encode()).hexdigest()[:16]


def new_session(sid: str, lang: str, pre_form: str, post_form: str, src: str | None, device: str, is_test: bool,
                network: str | None = None):
    with _lock, _conn() as c:
        c.execute("INSERT INTO learn_sessions(id, created_at, lang, pre_form, post_form, src, device, is_test, network)"
                  " VALUES (?,?,?,?,?,?,?,?,?)", (sid, time.time(), lang, pre_form, post_form, (src or "")[:24],
                                                 device, int(is_test), network or device))


def get_session(sid: str) -> sqlite3.Row | None:
    with _conn() as c:
        return c.execute("SELECT * FROM learn_sessions WHERE id=?", (sid,)).fetchone()


def save_pre(sid: str, answers: dict, scored: dict):
    with _lock, _conn() as c:
        c.execute("UPDATE learn_sessions SET pre_answers=?, pre_correct=?, pre_dangerous=?, pre_at=? WHERE id=?",
                  (json.dumps(answers), scored["correct"], scored["dangerous"], time.time(), sid))


def save_post(sid: str, answers: dict, scored: dict, per_concept: dict, state: str | None, role: str | None):
    with _lock, _conn() as c:
        c.execute("UPDATE learn_sessions SET post_answers=?, post_correct=?, post_dangerous=?, per_concept=?,"
                  " state=?, role=?, completed_at=? WHERE id=? AND completed_at IS NULL",
                  (json.dumps(answers), scored["correct"], scored["dangerous"], json.dumps(per_concept),
                   (state or "")[:40] or None, (role or "")[:24] or None, time.time(), sid))


def mark_shared(sid: str):
    with _lock, _conn() as c:
        c.execute("UPDATE learn_sessions SET shared=1 WHERE id=?", (sid,))


def network_completions_today(network: str | None) -> int:
    if not network:
        return 0
    since = time.time() - 86400
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM learn_sessions WHERE network=? AND completed_at>? AND is_test=0",
                         (network, since)).fetchone()[0]


def exclude(sid: str, reason: str):
    """Kept for transparency, but not counted in the public numbers."""
    with _lock, _conn() as c:
        c.execute("UPDATE learn_sessions SET excluded=? WHERE id=?", (reason, sid))


def excluded_counts() -> dict:
    with _conn() as c:
        rows = c.execute("SELECT excluded, COUNT(*) FROM learn_sessions WHERE completed_at IS NOT NULL AND is_test=0"
                         " AND excluded IS NOT NULL GROUP BY excluded").fetchall()
    return {r[0]: r[1] for r in rows}


def log_consult(lang: str, level: str, flags: list[str], parser: str, latency_ms: int, device: str, is_test: bool):
    with _lock, _conn() as c:
        c.execute("INSERT INTO consults(created_at, lang, level, flags, parser, latency_ms, device, is_test)"
                  " VALUES (?,?,?,?,?,?,?,?)", (time.time(), lang, level, json.dumps(flags), parser, latency_ms,
                                                device, int(is_test)))


def completed_sessions(include_test: bool = False) -> list[sqlite3.Row]:
    q = "SELECT * FROM learn_sessions WHERE completed_at IS NOT NULL"
    if not include_test:
        q += " AND is_test=0 AND excluded IS NULL"
    with _conn() as c:
        return c.execute(q + " ORDER BY completed_at").fetchall()


def started_count(include_test: bool = False) -> int:
    q = "SELECT COUNT(*) FROM learn_sessions" + ("" if include_test else " WHERE is_test=0")
    with _conn() as c:
        return c.execute(q).fetchone()[0]


def consult_rows(include_test: bool = False) -> list[sqlite3.Row]:
    q = "SELECT * FROM consults" + ("" if include_test else " WHERE is_test=0")
    with _conn() as c:
        return c.execute(q).fetchall()


def device_completions_today(device: str) -> int:
    since = time.time() - 86400
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM learn_sessions WHERE device=? AND completed_at>? AND is_test=0",
                         (device, since)).fetchone()[0]
