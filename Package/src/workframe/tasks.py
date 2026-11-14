"""Explicit generic task descriptions, separate from runtime dispatch state."""
import uuid
from .loading import resolve_script
from .wire import decode, encode, validate_task


class TaskSpec:
    """Capture a Python task file and an owned copy of JSON-compatible input.

    This describes one unit of execution, not a scheduling policy. Workload
    planners choose the payload, executor, and submission timing themselves.
    Public data access returns a copy so mutation does not alter a captured
    description or accidentally modify another derived task.
    """
    def __init__(self, script, data, task_id=None):
        self._script = resolve_script(script)
        self._id = uuid.uuid4().hex if task_id is None else task_id
        validate_task({"task_id": self._id, "script": str(self._script), "data": data})
        self._data_json = encode(data)

    @property
    def script(self):
        return self._script

    @property
    def task_id(self):
        return self._id

    @property
    def data(self):
        return decode(self._data_json)

    def to_dict(self):
        return {"task_id": self.task_id, "script": str(self.script), "data": self.data}

    def to_json(self):
        return encode(self.to_dict())

    @classmethod
    def from_dict(cls, value):
        validate_task(value)
        return cls(value["script"], value["data"], value["task_id"])

    @classmethod
    def from_json(cls, value):
        return cls.from_dict(decode(value))

    def with_data(self, data, task_id=None):
        return type(self)(self.script, data, task_id)

    def __repr__(self):
        return f"TaskSpec(script={self.script.name!r}, task_id={self.task_id!r})"
