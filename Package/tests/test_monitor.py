import subprocess
import sys
import time
from pathlib import Path
import pytest
from workframe import ResourceMonitor, Runtime, TaskSpec

TASK = Path(__file__).resolve().parents[1] / "examples/operation.py"


def test_monitor_is_in_memory_and_freezes_after_stop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with ResourceMonitor(interval=.02) as monitor:
        end = time.perf_counter() + .05
        while time.perf_counter() < end:
            pass
        value = monitor.snapshot()
        assert value["elapsed_seconds"] > 0
        assert value["cpu_seconds"] >= 0
        assert value["current_memory_bytes"] > 0
        assert value["process_count"] >= 1
    first = monitor.snapshot()
    time.sleep(.02)
    assert monitor.snapshot() == first
    assert list(tmp_path.iterdir()) == []


def test_monitor_includes_children():
    with ResourceMonitor(interval=.02) as monitor:
        child = subprocess.Popen([sys.executable, "-c", "import sys; sys.stdin.buffer.read(1)"], stdin=subprocess.PIPE)
        try:
            assert monitor.snapshot()["process_count"] >= 2
        finally:
            child.communicate(input=b"x", timeout=10)


def test_task_spec_and_runtime_resource_api():
    payload = {"values": [2, 3]}
    task = TaskSpec(TASK, payload, task_id="one")
    payload["values"].append(99)
    assert TaskSpec.from_json(task.to_json()).data == {"values": [2, 3]}
    with Runtime(1) as runtime:
        runtime.submit_task(0, task)
        assert runtime.receive(10)["result"] == 5
        assert runtime.resource_usage()["current_memory_bytes"] > 0
        assert "resources" in runtime.inspect()
    assert runtime.resource_usage()["running"] is False


def test_monitor_rejects_invalid_intervals():
    for value in (0, -1, float("nan"), True):
        with pytest.raises(ValueError):
            ResourceMonitor(interval=value)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows resource enforcement")
def test_launcher_does_not_require_a_report_file(tmp_path):
    script = tmp_path / "driver.py"
    script.write_text('print("driver completed")')
    value = subprocess.run([sys.executable, "-m", "workframe.launcher", str(script)],
                           cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert value.returncode == 0, value.stderr
    assert "CPU" in value.stdout
    assert not (tmp_path / "reports").exists()
