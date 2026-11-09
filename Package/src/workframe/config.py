"""Validated execution settings; these do not describe table schemas.

Execution settings configure transport and lifecycle mechanisms. Table
schemas and workload scheduling policies belong to the application.
"""
from dataclasses import asdict, dataclass, fields
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class ExecutionOptions:
    queue_capacity: int = 0
    receive_timeout: float = 30.0
    shutdown_timeout: float = 2.0
    max_message_bytes: int = 8 * 1024 * 1024
    event_capacity: int = 200
    entrypoint: str = "run"
    work_directory: str | None = None

    def __post_init__(self):
        integer_fields = {
            "queue_capacity": (self.queue_capacity, 0),
            "max_message_bytes": (self.max_message_bytes, 128),
            "event_capacity": (self.event_capacity, 1),
        }
        for name, (value, minimum) in integer_fields.items():
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} must be an integer >= {minimum}")
        for name in ("receive_timeout", "shutdown_timeout"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not isinstance(self.entrypoint, str) or not self.entrypoint.isidentifier():
            raise ValueError("entrypoint must be a Python identifier")
        if self.work_directory is not None:
            path = Path(self.work_directory).resolve(strict=True)
            if not path.is_dir():
                raise ValueError("work_directory must be a directory")
            object.__setattr__(self, "work_directory", str(path))

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict):
            raise ValueError("Execution options must be an object")
        names = {field.name for field in fields(cls)}
        unknown = set(value) - names
        if unknown:
            raise ValueError(f"Unknown execution settings: {sorted(unknown)}")
        return cls(**value)

    @classmethod
    def load(cls, path):
        with Path(path).open(encoding="utf-8") as stream:
            return cls.from_dict(json.load(stream))

    def save(self, path):
        from .metrics import save_report
        save_report(path, self.to_dict())

    def replace(self, **changes):
        value = self.to_dict()
        value.update(changes)
        return self.from_dict(value)

    def describe(self):
        return {
            "queue_capacity": "Messages per executor; zero leaves the queue unbounded",
            "receive_timeout": "Default seconds to wait for one completion",
            "shutdown_timeout": "Shared graceful-shutdown deadline in seconds",
            "max_message_bytes": "Maximum encoded UTF-8 bytes per task/result",
            "event_capacity": "Maximum metadata events retained in the driver",
            "entrypoint": "Callable name loaded from each task file",
            "work_directory": "Optional executor working directory",
        }
