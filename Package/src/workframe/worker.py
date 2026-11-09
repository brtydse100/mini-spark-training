import os
import time
import traceback
from .loading import load
from .wire import decode, encode, validate_task, success, failure
from .metrics import Stopwatch


def _pack(n, a, options):
    b = options.get("max_message_bytes", 8 * 1024 * 1024)
    timer = Stopwatch().start()
    try:
        f = load(a["script"], a.get("entrypoint", options.get("entrypoint", "run")))
        v = f(a["data"])
        m = timer.stop()
        m["pid"] = os.getpid()
        t = success(a["task_id"], n, v, m)
        s = encode(t, max_bytes=b)
    except Exception as e:
        m = timer.stop()
        m["pid"] = os.getpid()
        t = failure(a["task_id"], n, e, traceback.format_exc(), m)
        # Error detail itself may exceed a small message budget. Preserve
        # identity and type, then bound the diagnostic text before transport.
        try:
            s = encode(t, max_bytes=b)
        except ValueError:
            t["error"]["message"] = t["error"]["message"][:128]
            t["error"]["traceback"] = "Diagnostic truncated to fit message limit"
            s = encode(t)
    return s


def work(n, q, out, options=None):
    a = options or {}
    if a.get("work_directory"):
        os.chdir(a["work_directory"])
    while True:
        s = q.get()
        if s is None:
            break
        t = decode(s, max_bytes=a.get("max_message_bytes"))
        try:
            validate_task(t)
        except ValueError as e:
            # Runtime-generated messages always have identity. A malformed
            # message is not a workload failure that should crash silently.
            identity = t.get("task_id", "invalid") if isinstance(t, dict) else "invalid"
            if not isinstance(identity, str) or not identity:
                identity = "invalid"
            out.put(encode(failure(identity, n, e, traceback.format_exc())))
            continue
        out.put(_pack(n, t, a))
