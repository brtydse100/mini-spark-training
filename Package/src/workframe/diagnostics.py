"""Bounded metadata events for observing an execution.

Never store task inputs/results here. The event ring is deliberately bounded
so enabling diagnostics cannot turn a long session into an unbounded archive.
Instances are process-local and snapshots are copies, not live views.
"""
from collections import deque
import json
import os
from pathlib import Path
from threading import Lock
import time


class EventLog:
    def __init__(self, capacity=200):
        if type(capacity) is not int or capacity < 1:
            raise ValueError("Event capacity must be a positive integer")
        self.capacity = capacity
        self._items = deque(maxlen=capacity)
        self._lock = Lock()
        self._sequence = 0
        self._started = time.perf_counter()

    def record(self, event, **metadata):
        if not isinstance(event, str) or not event:
            raise ValueError("Event name must be nonempty text")
        allowed = (str, int, float, bool, type(None))
        if any(not isinstance(value, allowed) for value in metadata.values()):
            raise ValueError("Event metadata must contain scalar values only")
        reserved = {"event", "sequence", "elapsed_seconds", "pid"}
        if reserved & metadata.keys():
            raise ValueError("Reserved event metadata key")
        with self._lock:
            self._sequence += 1
            record = {
                "sequence": self._sequence,
                "elapsed_seconds": time.perf_counter() - self._started,
                "pid": os.getpid(),
                "event": event,
                **metadata,
            }
            # Reject non-finite metadata before appending it.
            json.dumps(record, allow_nan=False)
            self._items.append(record)

    def snapshot(self, event=None):
        with self._lock:
            return [dict(item) for item in self._items
                    if event is None or item["event"] == event]

    def clear(self):
        with self._lock:
            self._items.clear()

    def summary(self):
        with self._lock:
            return {
                "capacity": self.capacity,
                "retained": len(self._items),
                "total_recorded": self._sequence,
                "discarded": self._sequence - len(self._items),
            }

    def write(self, path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        records = self.snapshot()
        with target.open("w", encoding="utf-8", newline="\n") as stream:
            for record in records:
                stream.write(json.dumps(record, allow_nan=False) + "\n")

    def __len__(self):
        with self._lock:
            return len(self._items)
