from contextlib import contextmanager
from pathlib import Path
import sqlite3
from threading import RLock


class QuotaLedger:
    """SQLite counters shared by processes using the same Google project."""

    def __init__(self, path: str | Path = ":memory:"):
        self.connection = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS quota (day TEXT, bucket TEXT, count INTEGER, "
            "PRIMARY KEY(day, bucket))"
        )
        self.lock = RLock()

    @contextmanager
    def transaction(self):
        with self.lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                yield self.connection
                self.connection.commit()
            except BaseException:
                self.connection.rollback()
                raise

    def close(self):
        with self.lock:
            self.connection.close()
