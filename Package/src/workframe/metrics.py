"""Dependable timing, counters, and atomic report writing.

Stopwatch measures the calling process. Windows job accounting is separate
and covers descendants; do not sum worker wall times to obtain run duration.
Counters are explicit instrumentation: table logic chooses when to add rows.
"""
import json
import math
import os
from pathlib import Path
from threading import Lock
import time


class Stopwatch:
    def __init__(self):
        self._start = None
        self._cpu_start = None
        self._end = None
        self._cpu_end = None

    def start(self):
        if self._start is not None:
            raise RuntimeError("Stopwatch has already started")
        self._start = time.perf_counter()
        self._cpu_start = time.process_time()
        return self

    def stop(self):
        if self._start is None:
            raise RuntimeError("Stopwatch has not started")
        if self._end is None:
            self._end = time.perf_counter()
            self._cpu_end = time.process_time()
        return self.snapshot()

    def snapshot(self):
        if self._start is None:
            return {"elapsed_seconds": 0.0, "process_cpu_seconds": 0.0}
        end = self._end if self._end is not None else time.perf_counter()
        cpu = self._cpu_end if self._cpu_end is not None else time.process_time()
        return {
            "elapsed_seconds": max(0.0, end - self._start),
            "process_cpu_seconds": max(0.0, cpu - self._cpu_start),
        }

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()


class Counters:
    def __init__(self):
        self._values = {}
        self._lock = Lock()

    def add(self, name, value=1):
        if not isinstance(name, str) or not name:
            raise ValueError("Counter name must be nonempty text")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Counter increment must be numeric")
        if value < 0 or not math.isfinite(value):
            raise ValueError("Counter increment must be finite and nonnegative")
        with self._lock:
            self._values[name] = self._values.get(name, 0) + value
            return self._values[name]

    def snapshot(self):
        with self._lock:
            return dict(self._values)

    def reset(self):
        with self._lock:
            self._values.clear()

    def merge(self, snapshot, prefix=""):
        # Caller explicitly controls what is aggregated; no hidden worker state.
        for name, value in snapshot.items():
            self.add(prefix + name, value)



class SampleWindow:
    """A bounded window of scalar measurements, not task inputs or results.

    Summary statistics describe only the retained window. total_observations
    counts the lifetime stream, so callers can see when older samples have
    been discarded. Recording one measurement never grows storage past the
    configured capacity. Store only scalar measurements in this window;
    retain larger application values under a separate explicit policy.
    """
    def __init__(self, capacity=128):
        from collections import deque
        if type(capacity) is not int or capacity < 1:
            raise ValueError("Sample capacity must be a positive integer")
        self.capacity = capacity
        self._samples = deque(maxlen=capacity)
        self._count = 0
        self._lock = Lock()

    def record(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Sample must be numeric")
        if not math.isfinite(value) or value < 0:
            raise ValueError("Sample must be finite and nonnegative")
        with self._lock:
            self._samples.append(value)
            self._count += 1

    def snapshot(self):
        import statistics
        with self._lock:
            values = list(self._samples)
            total = self._count
        return {
            "capacity": self.capacity,
            "retained": len(values),
            "total_observations": total,
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None,
            "median": statistics.median(values) if values else None,
            "mean": statistics.fmean(values) if values else None,
        }

    def clear(self):
        with self._lock:
            self._samples.clear()
            self._count = 0

    def __len__(self):
        with self._lock:
            return len(self._samples)

def save_report(path, data):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=2, allow_nan=False)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    try:
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_report(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("A report must contain a JSON object")
    return data


def summarize_reports(paths):
    """Summarize repeats sharing a resource budget.

    This does not determine query correctness, equate different hardware, or
    distinguish warm/cold caches. The caller must control those conditions.
    Failed runs are counted, never silently treated as fast successful runs.
    """
    import statistics
    entries = [load_report(path) for path in paths]
    if not entries:
        raise ValueError("At least one report is required")
    budgets = {(r.get("cpu_percent"), r.get("memory_limit_bytes")) for r in entries}
    if len(budgets) != 1 or next(iter(budgets))[0] is None:
        raise ValueError("Reports must use the same explicit resource budget")
    good = [r for r in entries if r.get("status") == "success"]
    durations = []
    cpu = []
    peaks = []
    for report in good:
        for key in ("elapsed_seconds", "cpu_seconds", "peak_job_committed_bytes"):
            value = report.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Invalid report measurement: {key}")
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid report measurement: {key}")
        durations.append(report["elapsed_seconds"])
        cpu.append(report["cpu_seconds"])
        peaks.append(report["peak_job_committed_bytes"])
    percent, memory = next(iter(budgets))
    return {
        "total_runs": len(entries),
        "successful_runs": len(good),
        "failed_runs": len(entries) - len(good),
        "cpu_percent": percent,
        "memory_limit_bytes": memory,
        "median_elapsed_seconds": statistics.median(durations) if durations else None,
        "minimum_elapsed_seconds": min(durations) if durations else None,
        "maximum_elapsed_seconds": max(durations) if durations else None,
        "median_cpu_seconds": statistics.median(cpu) if cpu else None,
        "maximum_peak_job_committed_bytes": max(peaks) if peaks else None,
    }


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Summarize repeated benchmark reports")
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    value = summarize_reports(args.reports)
    if args.output:
        save_report(args.output, value)
    else:
        print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
