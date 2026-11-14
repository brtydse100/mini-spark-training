"""In-memory wall-clock, CPU, and memory observations for a process tree.

    Sampling does not enforce limits. The Windows Job Object integration in
    resources.py provides enforcement and OS-maintained whole-job accounting.
    A sampling monitor can miss short-lived processes or allocation spikes.
"""
import math
import os
from threading import Event, RLock, Thread
import time
from .process_tree import ProcessTree


class ResourceMonitor:
    """Observe the current program and descendants without creating files.

    CPU percent is average CPU consumption since start, normalized by logical
    machine capacity. cpu_seconds is cumulative observed user+kernel time.
    Retired process totals are folded into a scalar so history stays bounded
    by currently observed processes rather than all historical submissions.
    """
    def __init__(self, interval=.1, pid=None):
        if isinstance(interval, bool) or not isinstance(interval, (int, float)):
            raise ValueError("interval must be numeric")
        if not math.isfinite(interval) or interval < .01:
            raise ValueError("interval must be finite and at least 0.01 seconds")
        self.interval = interval
        self._tree = ProcessTree(pid)
        self._lock = RLock()
        self._stop = Event()
        self._thread = None
        self._started = None
        self._ended = None
        self._active = {}
        self._retired_cpu = 0.0
        self._cpu = 0.0
        self._memory = 0
        self._rss = 0
        self._peak = 0
        self._process_count = 0
        self._samples = 0
        self._access_errors = 0
        self._last_error = None
        self._capacity = os.cpu_count() or 1

    def _sample(self, baseline=False):
        with self._lock:
            observed = self._tree.observe()
            current = {item.identity: item for item in observed.processes}
            for identity in set(self._active) - set(current):
                start, last = self._active.pop(identity)
                self._retired_cpu += max(0.0, last - start)
            for identity, item in current.items():
                start = self._active.get(identity, (item.cpu_seconds if baseline else 0.0, 0.0))[0]
                self._active[identity] = start, item.cpu_seconds
            self._cpu = self._retired_cpu + sum(max(0.0, end-start) for start, end in self._active.values())
            self._memory = observed.memory_bytes
            self._rss = observed.rss_bytes
            self._peak = max(self._peak, self._memory)
            self._process_count = len(current)
            self._samples += 1
            self._access_errors += observed.access_errors

    def _run(self):
        while not self._stop.wait(self.interval):
            try:
                self._sample()
            except Exception as error:
                with self._lock:
                    self._last_error = f"{type(error).__name__}: {error}"

    def start(self):
        with self._lock:
            if self._started is not None:
                raise RuntimeError("Monitor has already started")
            self._started = time.perf_counter()
            self._sample(baseline=True)
            self._thread = Thread(target=self._run, name="workframe-resources", daemon=True)
            self._thread.start()
        return self

    def snapshot(self):
        with self._lock:
            if self._started is not None and self._ended is None:
                self._sample()
            end = self._ended if self._ended is not None else time.perf_counter()
            elapsed = 0.0 if self._started is None else max(0.0, end-self._started)
            return {
                "running": self._started is not None and self._ended is None,
                "elapsed_seconds": elapsed,
                "cpu_seconds": self._cpu,
                "cpu_percent": 0.0 if not elapsed else 100*self._cpu/elapsed/self._capacity,
                "current_memory_bytes": self._memory,
                "peak_sampled_memory_bytes": self._peak,
                "current_rss_bytes": self._rss,
                "memory_kind": self._tree.memory_kind,
                "process_count": self._process_count,
                "sample_count": self._samples,
                "sampling_access_errors": self._access_errors,
                "last_sampling_error": self._last_error,
            }

    def stop(self):
        with self._lock:
            if self._started is None:
                raise RuntimeError("Monitor has not started")
            if self._ended is not None:
                return self.snapshot()
        self._stop.set()
        self._thread.join(timeout=2)
        if self._thread.is_alive():
            raise RuntimeError("Monitor sampling thread did not stop")
        with self._lock:
            self._sample()
            self._ended = time.perf_counter()
            return self.snapshot()

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()
