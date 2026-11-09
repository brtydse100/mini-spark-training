"""Windows job-wide limits. Imported only by the trusted launcher."""
import os
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import time


@dataclass(frozen=True)
class Budget:
    cpu_percent: float = 50
    memory_mb: int = 512
    timeout: float = 120

    def __post_init__(self):
        for name in ("cpu_percent", "timeout"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not .01 <= self.cpu_percent <= 100:
            raise ValueError("CPU percent must be between 0.01 and 100")
        if type(self.memory_mb) is not int or self.memory_mb < 32:
            raise ValueError("Memory must be an integer of at least 32 MiB")

    @property
    def memory_bytes(self):
        return self.memory_mb * 1024 * 1024

    def to_dict(self):
        return asdict(self)

    @classmethod
    def load(cls, path):
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("Budget profile must be a JSON object")
        unknown = set(value) - {"cpu_percent", "memory_mb", "timeout"}
        if unknown:
            raise ValueError(f"Unknown budget fields: {sorted(unknown)}")
        return cls(**value)

    def override(self, **changes):
        value = self.to_dict()
        value.update({key: item for key, item in changes.items() if item is not None})
        return Budget(**value)


class Job:
    def __init__(self, cpu_percent, memory_mb):
        if os.name != "nt":
            raise OSError("Enforced benchmark runs require Windows")
        budget = Budget(cpu_percent, memory_mb)
        self.budget = budget
        import win32job
        self.api = win32job
        self.handle = win32job.CreateJobObject(None, "")
        try:
            info = win32job.QueryInformationJobObject(self.handle, win32job.JobObjectExtendedLimitInformation)
            info["BasicLimitInformation"]["LimitFlags"] = (win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | win32job.JOB_OBJECT_LIMIT_JOB_MEMORY)
            info["JobMemoryLimit"] = memory_mb * 1024 * 1024
            win32job.SetInformationJobObject(self.handle, win32job.JobObjectExtendedLimitInformation, info)
            # pywin32 does not expose CPU-rate information on every build.
            import ctypes
            from ctypes import wintypes
            class CpuRate(ctypes.Structure):
                _fields_ = [("flags", wintypes.DWORD), ("rate", wintypes.DWORD)]
            value = CpuRate(1 | 4, round(cpu_percent * 100))
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            setter = kernel.SetInformationJobObject
            setter.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
            setter.restype = wintypes.BOOL
            if not setter(int(self.handle), 15, ctypes.byref(value), ctypes.sizeof(value)):
                raise ctypes.WinError(ctypes.get_last_error())
        except BaseException:
            self.close()
            raise

    def assign(self, process):
        import win32api
        import win32con
        handle = win32api.OpenProcess(win32con.PROCESS_SET_QUOTA | win32con.PROCESS_TERMINATE, False, process.pid)
        try:
            self.api.AssignProcessToJobObject(self.handle, handle)
        finally:
            handle.Close()

    def sample(self):
        basic = self.api.QueryInformationJobObject(self.handle, self.api.JobObjectBasicAccountingInformation)
        extended = self.api.QueryInformationJobObject(self.handle, self.api.JobObjectExtendedLimitInformation)
        return {"cpu_seconds": (basic["TotalUserTime"] + basic["TotalKernelTime"]) / 10_000_000,
                "peak_job_committed_bytes": extended["PeakJobMemoryUsed"],
                "active_processes": basic["ActiveProcesses"],
                "total_processes": basic["TotalProcesses"]}

    def limits(self):
        """Read back enforced values rather than just reporting CLI requests."""
        import ctypes
        from ctypes import wintypes
        extended = self.api.QueryInformationJobObject(
            self.handle, self.api.JobObjectExtendedLimitInformation)
        value = (wintypes.DWORD * 2)()
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        query = kernel.QueryInformationJobObject
        query.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                          wintypes.DWORD, ctypes.c_void_p]
        query.restype = wintypes.BOOL
        if not query(int(self.handle), 15, value, ctypes.sizeof(value), None):
            raise ctypes.WinError(ctypes.get_last_error())
        return {
            "cpu_flags": value[0],
            "cpu_rate": value[1],
            "memory_limit_bytes": extended["JobMemoryLimit"],
            "limit_flags": extended["BasicLimitInformation"]["LimitFlags"],
        }

    def wait_empty(self, timeout=10):
        deadline = time.monotonic() + timeout
        while True:
            snapshot = self.sample()
            if snapshot["active_processes"] == 0:
                return snapshot
            if time.monotonic() >= deadline:
                raise TimeoutError("Job still contains active processes")
            time.sleep(.01)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def terminate(self):
        self.api.TerminateJobObject(self.handle, 1)

    def close(self):
        if self.handle is not None:
            self.handle.Close()
            self.handle = None
