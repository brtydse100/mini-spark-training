"""Read process-tree observations without controlling workload execution."""
from dataclasses import dataclass
import os
import psutil


@dataclass(frozen=True)
class ProcessUsage:
    pid: int
    created: float
    cpu_seconds: float
    memory_bytes: int
    rss_bytes: int

    @property
    def identity(self):
        # A recycled PID is a new process, not a continuation of old counters.
        return self.pid, self.created


@dataclass(frozen=True)
class TreeObservation:
    processes: tuple
    access_errors: int

    @property
    def memory_bytes(self):
        return sum(item.memory_bytes for item in self.processes)

    @property
    def rss_bytes(self):
        return sum(item.rss_bytes for item in self.processes)


class ProcessTree:
    """A process and its recursive descendants, identified by PID/create time.

    Windows private committed memory is used for the primary memory measure.
    On other systems the primary measure falls back to RSS. Summed RSS can
    count shared pages more than once, so it is exposed separately.
    """
    def __init__(self, pid=None):
        pid = os.getpid() if pid is None else pid
        if type(pid) is not int or pid < 1:
            raise ValueError("pid must be a positive integer")
        self.root = psutil.Process(pid)
        self.memory_kind = "private_committed" if os.name == "nt" else "rss"

    def observe(self):
        errors = 0
        try:
            processes = [self.root, *self.root.children(recursive=True)]
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            return TreeObservation((), 0)
        except psutil.AccessDenied:
            processes = [self.root]
            errors += 1
        values = {}
        for process in processes:
            try:
                with process.oneshot():
                    created = process.create_time()
                    cpu = process.cpu_times()
                    memory = process.memory_info()
                item = ProcessUsage(
                    process.pid, created, cpu.user + cpu.system,
                    getattr(memory, "private", memory.rss), memory.rss,
                )
                values[item.identity] = item
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
            except psutil.AccessDenied:
                errors += 1
        return TreeObservation(tuple(values.values()), errors)
