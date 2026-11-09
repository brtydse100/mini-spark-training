"""Instructor-only repair. Never include in trainee archives."""
from pathlib import Path
import queue
import uuid
from workframe import Runtime, TaskError
from workframe.wire import encode, decode


def capacity(value):
    if isinstance(value, bool):
        raise ValueError("Boolean capacity is invalid")
    try:
        from decimal import Decimal
        n = Decimal(str(value))
        if not n.is_finite() or n != n.to_integral_value() or n < 1:
            raise ValueError("Capacity must be a positive integer")
        return int(n)
    except (ArithmeticError, TypeError) as exc:
        raise ValueError("Invalid capacity") from exc


class FixedRuntime(Runtime):
    def _do(self, v, a=None, b=None, c=None, d=None):
        if v == "send":
            if not self._p:
                raise RuntimeError("Start the runtime first")
            if type(a) is not int or not 0 <= a < self.n:
                raise ValueError("Unknown executor")
            task_id = d or uuid.uuid4().hex
            if not isinstance(task_id, str) or task_id in self._x:
                raise ValueError("Task identity must be a unique active string")
            payload = encode({"task_id": task_id, "script": str(Path(b).resolve(strict=True)), "data": c})
            self._x[task_id] = a
            self._q[a].put(payload)
            return task_id
        if v == "get":
            try:
                result = decode(self._out.get(timeout=a))
            except queue.Empty:
                raise TimeoutError("No result arrived") from None
            if self._x.get(result["task_id"]) != result["executor"]:
                raise RuntimeError("Unknown task or wrong executor")
            del self._x[result["task_id"]]
            if result["status"] == "error":
                raise TaskError(result)
            return result
        if v == "many":
            from itertools import islice
            return [self._do("send", a, t["script"], t["data"], t.get("task_id")) for t in islice(b, capacity(d))]
        if v == "state":
            return len(self._x)
        raise ValueError(v)
