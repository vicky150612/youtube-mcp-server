from collections import OrderedDict
from datetime import timedelta
from threading import RLock

from youtube_mcp.clock import SystemClock

MAX_TTL = timedelta(hours=24)


class TTLStore:
    def __init__(self, clock=None, *, ttl=MAX_TTL, capacity=4096):
        if not timedelta(0) < ttl <= MAX_TTL or capacity < 1:
            raise ValueError("Public cache TTL must be positive and at most 24 hours.")
        self.clock = clock or SystemClock()
        self.ttl = ttl
        self.capacity = capacity
        self.entries = OrderedDict()
        self.lock = RLock()

    def get(self, key):
        with self.lock:
            entry = self.entries.get(key)
            if entry is None:
                return None
            created, value = entry
            if not timedelta(0) <= self.clock.now() - created < self.ttl:
                del self.entries[key]
                return None
            self.entries.move_to_end(key)
            return value

    def put(self, key, value):
        with self.lock:
            self.entries[key] = (self.clock.now(), value)
            self.entries.move_to_end(key)
            if len(self.entries) > self.capacity:
                self.entries.popitem(last=False)
