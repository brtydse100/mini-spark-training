"""Local execution skeleton. Query and table logic belongs to the trainee.

Runtime provides explicit process/transport primitives. ExecutionOptions
configures those primitives without choosing a scheduling policy. The
separate launcher applies a shared Windows resource budget.
"""
from .runtime import Runtime
from .errors import TaskError, ProtocolError, TaskLoadError, ExecutorStopped
from .config import ExecutionOptions
from .diagnostics import EventLog
from .metrics import Stopwatch, Counters

__all__ = [
    "Runtime",
    "TaskError",
    "ProtocolError",
    "TaskLoadError",
    "ExecutorStopped",
    "ExecutionOptions",
    "EventLog",
    "Stopwatch",
    "Counters",
]
