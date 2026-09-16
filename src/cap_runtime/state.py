"""Private metadata store. No message bodies, subject lines, or credentials."""

import hashlib
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path

from cap_runtime.models import CAPError


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


class State:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)
        self.path = directory / "state.sqlite3"
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        os.chmod(self.path, 0o600)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token TEXT PRIMARY KEY, binding TEXT NOT NULL,
                    kind TEXT NOT NULL, payload TEXT NOT NULL, expires REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS seen (
                    binding TEXT NOT NULL, item TEXT NOT NULL, revision TEXT NOT NULL,
                    PRIMARY KEY(binding, item)
                );
            """)

    def connect(self):
        # Caller must use `with`; isolation protects each acknowledgement transaction.
        from contextlib import contextmanager

        @contextmanager
        def connection():
            db = sqlite3.connect(self.path, timeout=10)
            try:
                with db:
                    yield db
            finally:
                db.close()

        return connection()

    def issue(self, binding: str, kind: str, payload: dict, ttl: int = 3600) -> str:
        token = secrets.token_urlsafe(24)
        with self.connect() as db:
            db.execute("DELETE FROM tokens WHERE expires < ?", (time.time(),))
            db.execute(
                "INSERT INTO tokens VALUES (?, ?, ?, ?, ?)",
                (token, binding, kind, json.dumps(payload), time.time() + ttl),
            )
        return token

    def read(self, token: str, binding: str, kind: str) -> dict:
        with self.connect() as db:
            row = db.execute(
                "SELECT payload FROM tokens WHERE token=? AND binding=? AND kind=? AND expires>?",
                (token, binding, kind, time.time()),
            ).fetchone()
        if row is None:
            raise CAPError(
                "invalid_cursor", "Token expired or belongs to a different request/account."
            )
        return json.loads(row[0])

    def unseen(self, binding: str, revisions: list[tuple[str, str]]) -> list[str]:
        with self.connect() as db:
            return [
                item
                for item, rev in revisions
                if db.execute(
                    "SELECT 1 FROM seen WHERE binding=? AND item=? AND revision=?",
                    (binding, item, rev),
                ).fetchone()
                is None
            ]

    def acknowledge(self, token: str, binding: str) -> int:
        # Atomic acknowledgement and token consumption, safe across processes/restarts.
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT payload FROM tokens WHERE token=? AND binding=? AND kind='batch' "
                "AND expires>?",
                (token, binding, time.time()),
            ).fetchone()
            if row is None:
                raise CAPError(
                    "invalid_batch", "Batch expired, already acknowledged, or wrong scope."
                )
            payload = json.loads(row[0])
            db.executemany(
                "INSERT OR REPLACE INTO seen VALUES (?, ?, ?)",
                [(binding, item, rev) for item, rev in payload["revisions"]],
            )
            db.execute("DELETE FROM tokens WHERE token=?", (token,))
        return len(payload["revisions"])
