from pathlib import Path
import pytest
from workframe import Runtime, TaskError
from workframe.settings import amount

SCRIPT = (Path(__file__).resolve().parents[2] / "Package") / "examples" / "operation.py"

def test_two_workers_and_zero():
    with Runtime(2) as r:
        r.submit(0, SCRIPT, {"values": [1, 2]}, "a")
        r.submit(1, SCRIPT, {"values": []}, "b")
        assert {r.receive(10)["result"], r.receive(10)["result"]} == {0, 3}

def test_exception_and_timeout(tmp_path):
    script = tmp_path / "task.py"
    script.write_text('def run(data):\n    raise ValueError("broken input")\n')
    with Runtime(1) as r:
        with pytest.raises(TimeoutError):
            r.receive(.05)
        r.submit(0, script, {}, "bad")
        with pytest.raises(TaskError, match="broken input"):
            r.receive(10)

def test_strict_json_error():
    with Runtime(1) as r:
        with pytest.raises(ValueError):
            r.submit(0, SCRIPT, {"values": [float("nan")]}, "nan")

@pytest.mark.xfail(strict=True, reason="Teaching defect: task identity tracked by worker")
def test_pipelined_tasks():
    with Runtime(1) as r:
        r.submit(0, SCRIPT, {"values": [1]}, "a")
        r.submit(0, SCRIPT, {"values": [2]}, "b")
        assert [r.receive(10)["result"], r.receive(10)["result"]] == [1, 2]

@pytest.mark.xfail(strict=True, reason="Teaching defect: completed IDs reused as cached answers")
def test_repeated_execution():
    with Runtime(1) as r:
        r.submit(0, SCRIPT, {"values": [1]}, "a")
        assert r.receive(10)["result"] == 1
        r.submit(0, SCRIPT, {"values": [9]}, "a")
        assert r.receive(10)["result"] == 9

@pytest.mark.xfail(strict=True, reason="Teaching defect: submissions retained after completion")
def test_payload_release():
    with Runtime(1) as r:
        r.submit(0, SCRIPT, {"values": [1] * 100}, "a")
        r.receive(10)
        assert not r._history

@pytest.mark.xfail(strict=True, reason="Teaching defect: configuration not normalized")
def test_numeric_contract():
    assert type(amount("4")) is int
    assert type(amount(4.0)) is int
