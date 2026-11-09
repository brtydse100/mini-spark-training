"""Generic failure values, independent of the workload being executed."""
from copy import deepcopy


class TaskError(RuntimeError):
    def __init__(self, message):
        self.message = deepcopy(message)
        detail = message.get("error", {})
        identity = message.get("task_id", "unknown")
        kind = detail.get("type", "TaskFailure")
        text = detail.get("message", "No error detail")
        super().__init__(f"Task {identity}: {kind}: {text}")

    @property
    def task_id(self):
        return self.message.get("task_id")

    @property
    def executor(self):
        return self.message.get("executor")

    @property
    def remote_traceback(self):
        return self.message.get("error", {}).get("traceback", "")

    @property
    def error_type(self):
        return self.message.get("error", {}).get("type", "TaskFailure")

    def to_dict(self):
        return deepcopy(self.message)


class ProtocolError(ValueError):
    """A message cannot be interpreted as a task or completion."""


class TaskLoadError(ValueError):
    """A task file exists but does not expose a usable entry point."""


class ExecutorStopped(RuntimeError):
    def __init__(self, executors):
        self.executors = list(executors)
        super().__init__(f"Executors exited: {self.executors}")
