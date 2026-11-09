import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

@pytest.mark.skipif(os.name != "nt", reason="Windows enforcement")
def test_launcher_report_and_timeout(tmp_path):
    script = tmp_path / "ok.py"
    script.write_text('print("hello")')
    report = tmp_path / "report.json"
    result = subprocess.run([sys.executable, "-m", "workframe.launcher", "--cpu-percent", "25", "--memory-mb", "256", "--report", str(report), str(script)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    data = json.loads(report.read_text())
    assert data["status"] == "success"
    assert data["elapsed_seconds"] > 0
    assert data["peak_job_committed_bytes"] > 0
    script.write_text('import time\ntime.sleep(30)')
    result = subprocess.run([sys.executable, "-m", "workframe.launcher", "--timeout", "0.3", "--report", str(report), str(script)], capture_output=True, text=True, timeout=20)
    assert result.returncode != 0
    assert json.loads(report.read_text())["status"] == "timeout"


@pytest.mark.skipif(os.name != "nt", reason="Windows enforcement")
def test_cpu_configuration_and_memory_rejection(tmp_path):
    import ctypes
    from ctypes import wintypes
    from workframe.resources import Job
    job = Job(12.5, 128)
    try:
        value = (wintypes.DWORD * 2)()
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        query = kernel.QueryInformationJobObject
        query.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
        query.restype = wintypes.BOOL
        assert query(int(job.handle), 15, value, ctypes.sizeof(value), None)
        assert list(value) == [5, 1250]
    finally:
        job.close()
    script = tmp_path / "memory.py"
    script.write_text('try:\n    x = bytearray(256*1024*1024)\nexcept MemoryError:\n    print("ALLOCATION_REJECTED")\nelse:\n    raise RuntimeError("Budget was not enforced")')
    report = tmp_path / "memory.json"
    run = subprocess.run([sys.executable, "-m", "workframe.launcher", "--memory-mb", "128", "--report", str(report), str(script)], capture_output=True, text=True, timeout=20)
    assert run.returncode == 0, run.stderr
    assert "ALLOCATION_REJECTED" in run.stdout
    data = json.loads(report.read_text())
    assert data["memory_limit_bytes"] == 128*1024*1024
    assert data["peak_job_committed_bytes"] > 0

@pytest.mark.skipif(os.name != "nt", reason="Windows enforcement")
def test_descendant_is_accounted_and_cleaned(tmp_path):
    script = tmp_path / "orphan.py"
    script.write_text('import subprocess, sys\nsubprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])')
    report = tmp_path / "tree.json"
    run = subprocess.run([sys.executable, "-m", "workframe.launcher", "--report", str(report), str(script)], capture_output=True, text=True, timeout=20)
    data = json.loads(report.read_text())
    assert run.returncode != 0
    assert data["status"] == "orphan_processes"
    assert data["total_processes"] >= 2
