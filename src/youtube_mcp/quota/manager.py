from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from youtube_mcp.clock import SystemClock
from youtube_mcp.errors import OverBudgetError, UnknownCostError
from youtube_mcp.models import QuotaCost, QuotaStatus
from youtube_mcp.quota.ledger import QuotaLedger

PACIFIC = ZoneInfo("America/Los_Angeles")
COSTS = {
    **dict.fromkeys(("videos.list", "channels.list", "playlistItems.list",
                     "playlists.list", "subscriptions.list", "videoCategories.list"), (1, 0, 0)),
    "search.list": (0, 1, 0),
    "videos.insert": (0, 0, 1),
    "playlists.insert": (50, 0, 0),
    "playlistItems.insert": (50, 0, 0),
}
BUCKETS = ("general", "search", "videos_insert")


class QuotaManager:
    def __init__(self, ledger: QuotaLedger, clock=None, *, general=10_000, search=100,
                 videos_insert=100):
        self.ledger = ledger
        self.clock = clock or SystemClock()
        self.limits = (general, search, videos_insert)
        if any(type(limit) is not int or limit < 0 for limit in self.limits):
            raise ValueError("Quota limits must be nonnegative integers.")
        self._tool_search = ContextVar("tool_search", default=None)

    def cost_of(self, op: str, *, calls: int = 1) -> QuotaCost:
        if op not in COSTS or type(calls) is not int or calls < 1:
            raise UnknownCostError("The operation or request count has no known cost.")
        return QuotaCost(*(value * calls for value in COSTS[op]))

    @contextmanager
    def tool_scope(self):
        """Wrap one MCP invocation to count search across all provider methods."""
        if self._tool_search.get() is not None:
            yield
            return
        token = self._tool_search.set(0)
        try:
            yield
        finally:
            self._tool_search.reset(token)

    @staticmethod
    def _remaining(connection, day, limits):
        counts = dict(connection.execute("SELECT bucket, count FROM quota WHERE day=?", (day,)))
        return tuple(max(0, limit - counts.get(bucket, 0))
                     for bucket, limit in zip(BUCKETS, limits, strict=True))

    def _charge(self, cost, *, record):
        units = (cost.general, cost.search, cost.videos_insert)
        if any(type(unit) is not int or unit < 0 for unit in units):
            raise UnknownCostError("Invalid quota cost.")
        used_search = self._tool_search.get()
        if used_search is not None and used_search + cost.search > 2:
            raise OverBudgetError("This tool invocation permits at most two search pages.")
        with self.ledger.transaction() as connection:
            day = self.clock.now().astimezone(PACIFIC).date().isoformat()
            remaining = self._remaining(connection, day, self.limits)
            if any(unit > left for unit, left in zip(units, remaining, strict=True)):
                raise OverBudgetError("The required YouTube quota exceeds the remaining budget.")
            if record:
                connection.executemany(
                    "INSERT INTO quota VALUES (?, ?, ?) ON CONFLICT(day, bucket) "
                    "DO UPDATE SET count=count+excluded.count",
                    [(day, bucket, unit) for bucket, unit in zip(BUCKETS, units, strict=True) if unit],
                )
        if record and used_search is not None:
            self._tool_search.set(used_search + cost.search)
        return day

    def check(self, cost: QuotaCost) -> None:
        self._charge(cost, record=False)

    def record(self, cost: QuotaCost) -> str:
        # Atomically reserve before sending. Ambiguous network failures remain charged.
        return self._charge(cost, record=True)

    def mark_exhausted(self, bucket, *, day=None):
        limit = self.limits[BUCKETS.index(bucket)]
        with self.ledger.transaction() as connection:
            day = day or self.clock.now().astimezone(PACIFIC).date().isoformat()
            connection.execute(
                "INSERT INTO quota VALUES (?, ?, ?) ON CONFLICT(day, bucket) "
                "DO UPDATE SET count=max(count, excluded.count)", (day, bucket, limit)
            )

    def status(self) -> QuotaStatus:
        with self.ledger.transaction() as connection:
            day = self.clock.now().astimezone(PACIFIC).date()
            general, search, uploads = self._remaining(connection, day.isoformat(), self.limits)
        reset = datetime.combine(day + timedelta(days=1), time.min, tzinfo=PACIFIC)
        return QuotaStatus(general, search, reset, uploads)
