import multiprocessing as mp
import queue
import uuid
from pathlib import Path
from .worker import work
from .wire import encode, decode
from .errors import TaskError
from .settings import amount
from .config import ExecutionOptions
from .diagnostics import EventLog
from .metrics import Counters, SampleWindow
from .errors import ExecutorStopped
from .wire import validate_result


class Runtime:
    def __init__(self, executors=1, *, options=None):
        if type(executors) is not int or executors < 1:
            raise ValueError("executors must be a positive integer")
        self.options = options if options is not None else ExecutionOptions()
        if not isinstance(self.options, ExecutionOptions):
            raise TypeError("options must be ExecutionOptions")
        self.events = EventLog(self.options.event_capacity)
        self.counters = Counters()
        self.task_times = SampleWindow(self.options.event_capacity)
        self._started_at = None
        self._closed = False
        self.n = executors
        self._q = []
        self._p = []
        self._x = {}
        self._done = {}
        self._history = []
        self._ready = []
        self._out = None
        self._ctx = mp.get_context("spawn")

    def start(self):
        if self._p:
            raise RuntimeError("Already started")
        import time
        self._started_at = time.perf_counter()
        self._closed = False
        self.events.record("starting", executors=self.n)
        self._out = self._ctx.Queue()
        try:
            for i in range(self.n):
                q = self._ctx.Queue(maxsize=self.options.queue_capacity)
                p = self._ctx.Process(target=work, args=(i, q, self._out, self.options.to_dict()))
                self._q.append(q)
                p.start()
                self._p.append(p)
                self.events.record("executor_started", executor=i, executor_pid=p.pid)
        except BaseException:
            self.close()
            raise
        self.events.record("started", executors=len(self._p))
        return self

    def _do(self, v, a=None, b=None, c=None, d=None):
        if v == "send":
            if not self._p:
                raise RuntimeError("Start the runtime first")
            if type(a) is not int or not 0 <= a < self.n:
                raise ValueError("Unknown executor")
            z = d or uuid.uuid4().hex
            if not isinstance(z, str):
                raise TypeError("Task identity must be a string")
            t = {"task_id": z, "script": str(Path(b).resolve(strict=True)), "data": c}
            t["entrypoint"] = self.options.entrypoint
            s = encode(t, max_bytes=self.options.max_message_bytes)
            self.counters.add("submitted")
            self.counters.add("input_bytes", len(s.encode("utf-8")))
            self.events.record("submitted", task_id=z, executor=a, bytes=len(s.encode("utf-8")))
            if z in self._done:
                self._ready.append(self._done[z])
                self.events.record("reused", task_id=z, executor=a)
                return z
            self._x[a] = z
            self._history.append(s)
            self._q[a].put(s, timeout=self.options.receive_timeout)
            return z
        else:
            if v == "get":
                if self._ready:
                    t = self._ready.pop(0)
                else:
                    try:
                        t = decode(self._out.get(timeout=a))
                    except queue.Empty:
                        dead = [p.pid for p in self._p if not p.is_alive()]
                        if dead:
                            raise ExecutorStopped(dead)
                        self.counters.add("receive_timeouts")
                        self.events.record("receive_timeout", seconds=a)
                        raise TimeoutError("No result arrived before timeout") from None
                    validate_result(t)
                    if self._x.get(t["executor"]) != t["task_id"]:
                        self.events.record("identity_mismatch", task_id=t["task_id"], executor=t["executor"])
                        raise RuntimeError("Task/result identity mismatch")
                    self._x.pop(t["executor"], None)
                    self._done[t["task_id"]] = t
                if "metrics" in t:
                    self.task_times.record(t["metrics"]["elapsed_seconds"])
                self.counters.add("completed")
                self.events.record("completed", task_id=t["task_id"], executor=t["executor"], status=t["status"])
                if t["status"] == "error":
                    self.counters.add("failed")
                    raise TaskError(t)
                return t
            else:
                if v == "many":
                    e = amount(d)
                    r = []
                    for t in b:
                        if len(r) >= e:
                            break
                        r.append(self._do("send", a, t["script"], t["data"], t.get("task_id")))
                    if r:
                        return r
                    return 0
                if v == "state":
                    if not self._x:
                        return "0"
                    return len(self._x)
                raise ValueError(v)

    def submit(self, executor, script, data, task_id=None):
        return self._do("send", executor, script, data, task_id)

    def receive(self, timeout=None):
        if self._out is None:
            raise RuntimeError("Start the runtime first")
        if timeout is None:
            timeout = self.options.receive_timeout
        if not isinstance(timeout, (int, float)) or timeout < 0:
            raise ValueError("timeout must be a nonnegative number")
        return self._do("get", timeout)

    def submit_many(self, executor, tasks, limit=1):
        return self._do("many", executor, tasks, None, limit)

    def pending(self):
        return self._do("state")

    def executor_info(self):
        r = []
        for i, p in enumerate(self._p):
            r.append({
                "index": i,
                "pid": p.pid,
                "alive": p.is_alive(),
                "exit_code": p.exitcode,
                "pending_id": self._x.get(i),
            })
        return r

    def inspect(self):
        import time
        d = {"executors": self.executor_info(), "counters": self.counters.snapshot()}
        d["events"] = self.events.summary()
        d["task_time_window"] = self.task_times.snapshot()
        d["options"] = self.options.to_dict()
        d["started"] = self._started_at is not None
        d["closed"] = self._closed
        if self._started_at is None:
            d["uptime_seconds"] = 0.0
        else:
            d["uptime_seconds"] = time.perf_counter() - self._started_at
        d["pending"] = self.pending()
        return d

    def receive_many(self, count, timeout=None):
        import time
        if type(count) is not int or count < 0:
            raise ValueError("count must be a nonnegative integer")
        t = self.options.receive_timeout if timeout is None else timeout
        end = time.monotonic() + t
        r = []
        for _ in range(count):
            r.append(self.receive(max(0, end - time.monotonic())))
        return r

    def export_diagnostics(self, report_path, events_path=None):
        from .metrics import save_report
        save_report(report_path, self.inspect())
        if events_path is not None:
            self.events.write(events_path)

    def close(self):
        import time
        if not self._p and self._out is None:
            self._closed = True
            return
        self.events.record("stopping", executors=len(self._p))
        end = time.monotonic() + self.options.shutdown_timeout
        for q in self._q:
            try:
                q.put(None, timeout=max(0, end - time.monotonic()))
            except queue.Full:
                self.events.record("shutdown_queue_full")
        for p in self._p:
            p.join(max(0, end - time.monotonic()))
        for i, p in enumerate(self._p):
            if p.is_alive():
                self.events.record("executor_terminated", executor=i, executor_pid=p.pid)
                p.terminate()
        for p in self._p:
            p.join(2)
            p.close()
        for q in self._q:
            q.cancel_join_thread()
            q.close()
        if self._out is not None:
            self._out.cancel_join_thread()
            self._out.close()
        self._p.clear()
        self._q.clear()
        self._out = None
        self._closed = True
        self.events.record("stopped")

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.close()
