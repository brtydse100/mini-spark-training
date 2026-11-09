from pathlib import Path
import pytest
from workframe import Runtime, TaskError

TASK = Path(__file__).resolve().parents[1] / "examples/operation.py"


def test_local_tasks_return_json_values():
    with Runtime(2) as runtime:
        runtime.submit(0, TASK, {"values": [1, 2]}, "sum")
        runtime.submit(1, TASK, {"values": []}, "empty")
        messages = runtime.receive_many(2, timeout=10)
        assert {m["task_id"]: m["result"] for m in messages} == {"sum": 3, "empty": 0}


def test_task_exception_preserves_identity(tmp_path):
    task = tmp_path / "error_task.py"
    task.write_text('def run(data):\n    raise ValueError("invalid input")\n')
    with Runtime(1) as runtime:
        runtime.submit(0, task, {}, "failure")
        with pytest.raises(TaskError) as caught:
            runtime.receive(10)
        assert caught.value.task_id == "failure"
        assert "invalid input" in caught.value.remote_traceback
