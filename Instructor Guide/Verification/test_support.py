import json
import time
from pathlib import Path
import pytest
from workframe.config import ExecutionOptions
from workframe.diagnostics import EventLog
from workframe.metrics import Stopwatch, Counters
from workframe.loading import inspect_task
from workframe.wire import decode, encode, validate_task, validate_result
from workframe import Runtime

TASK = (Path(__file__).resolve().parents[2] / "Package") / "examples/operation.py"

def test_options_roundtrip_and_validation(tmp_path):
    config = ExecutionOptions(queue_capacity=2, receive_timeout=3)
    path = tmp_path / "config.json"
    config.save(path)
    assert ExecutionOptions.load(path) == config
    with pytest.raises(ValueError):
        ExecutionOptions(queue_capacity=-1)
    with pytest.raises(ValueError):
        ExecutionOptions.from_dict({"mystery": 1})
    with pytest.raises(ValueError):
        ExecutionOptions(receive_timeout=float("nan"))

def test_bounded_events_do_not_hold_payloads(tmp_path):
    events = EventLog(capacity=2)
    events.record("submitted", task_id="a", bytes=100)
    events.record("completed", task_id="a")
    events.record("submitted", task_id="b")
    snapshot = events.snapshot()
    assert len(snapshot) == 2
    snapshot[0]["event"] = "changed"
    assert events.snapshot()[0]["event"] == "completed"
    path = tmp_path / "events.jsonl"
    events.write(path)
    assert len(path.read_text().splitlines()) == 2

def test_measurement_and_counters():
    with Stopwatch() as timer:
        time.sleep(.002)
    first = timer.snapshot()
    time.sleep(.002)
    assert timer.snapshot() == first
    assert first["elapsed_seconds"] > 0
    counters = Counters()
    counters.add("rows", 3)
    assert counters.snapshot() == {"rows": 3}
    with pytest.raises(ValueError):
        counters.add("rows", -1)

def test_protocol_and_inspection():
    assert inspect_task(TASK)["entrypoint"] == "run"
    with pytest.raises(ValueError):
        decode('{"value": NaN}')
    with pytest.raises(ValueError):
        encode({"large": "x" * 100}, max_bytes=10)
    with pytest.raises(ValueError):
        validate_task({"script": "x"})
    with pytest.raises(ValueError):
        validate_result({"task_id": "a", "status": "ok"})

def test_runtime_options_and_diagnostics():
    with Runtime(1, options=ExecutionOptions(queue_capacity=2)) as runtime:
        runtime.submit(0, TASK, {"values": [2, 3]}, "a")
        result = runtime.receive()
        assert result["result"] == 5
        assert result["metrics"]["elapsed_seconds"] >= 0
        snapshot = runtime.inspect()
        assert snapshot["counters"]["submitted"] == 1
        assert snapshot["counters"]["completed"] == 1
        assert snapshot["executors"][0]["alive"]
        assert runtime.events.snapshot()


def test_budget_profile_and_summary(tmp_path):
    from workframe.resources import Budget
    from workframe.metrics import save_report, summarize_reports
    profile = tmp_path / "budget.json"
    profile.write_text('{"cpu_percent":25,"memory_mb":256,"timeout":30}')
    budget = Budget.load(profile)
    assert budget.cpu_percent == 25
    assert budget.memory_bytes == 256 * 1024 * 1024
    with pytest.raises(ValueError):
        Budget(cpu_percent=101)
    with pytest.raises(ValueError):
        Budget(memory_mb=True)
    reports = []
    for n in [3, 1, 2]:
        path = tmp_path / f"run{n}.json"
        save_report(path, {"status":"success", "elapsed_seconds":n,
            "cpu_percent":25, "memory_limit_bytes":budget.memory_bytes,
            "cpu_seconds":.5, "peak_job_committed_bytes":1000})
        reports.append(path)
    summary = summarize_reports(reports)
    assert summary["median_elapsed_seconds"] == 2
    assert summary["successful_runs"] == 3
    with pytest.raises(ValueError):
        summarize_reports([])


def test_bounded_timing_window():
    from workframe.metrics import SampleWindow
    samples = SampleWindow(capacity=3)
    for value in (1, 2, 3, 4):
        samples.record(value)
    summary = samples.snapshot()
    assert summary["total_observations"] == 4
    assert summary["retained"] == 3
    assert summary["median"] == 3
    assert summary["minimum"] == 2
    with pytest.raises(ValueError):
        samples.record(float("inf"))


def test_custom_entrypoint_and_error_metadata(tmp_path):
    script = tmp_path / "task.py"
    script.write_text('def execute(data):\n    return data["value"] * 2\n')
    with Runtime(1, options=ExecutionOptions(entrypoint="execute")) as runtime:
        runtime.submit(0, script, {"value": 4}, "custom")
        assert runtime.receive()["result"] == 8
        script.write_text('def execute(data):\n    raise ValueError("bad value")\n')
        runtime.submit(0, script, {}, "failure")
        from workframe import TaskError
        with pytest.raises(TaskError) as failure:
            runtime.receive()
        assert failure.value.task_id == "failure"
        assert failure.value.error_type == "ValueError"
        assert "bad value" in failure.value.remote_traceback
