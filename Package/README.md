# Workframe

Workframe runs local Python tasks in separate executor processes. A driver
submits JSON-compatible inputs with a Python file path and receives completion
messages containing a result or error. It includes execution options,
diagnostics, task timing, and a Windows launcher with process-tree resource
limits.

## Install

Requires Python 3.11 or newer. Windows 10/11 supports the resource-controlled
launcher. Install from this directory:

```powershell
python -m pip install .
```

For development, see [CONTRIBUTING.md](CONTRIBUTING.md). After setup, use
`scripts/check.ps1` for the editable install, `scripts/build.ps1` to create
wheel/source archives, or `scripts/test-wheel.ps1` to build and test the wheel
in a separate environment.

## Run a task

Create a Python file named task.py:

```python
def run(data):
    return sum(data["values"])
```

Create driver.py beside it:

```python
from pathlib import Path
from workframe import Runtime


def main():
    task = Path(__file__).with_name("task.py")
    with Runtime(2) as runtime:
        runtime.submit(0, task, {"values": [1, 2, 3]}, task_id="first")
        runtime.submit(1, task, {"values": [4, 5]}, task_id="second")
        for message in runtime.receive_many(2):
            print(message["task_id"], message["result"])


if __name__ == "__main__":
    main()
```

Run `python driver.py`. A task entry point accepts one data argument and
returns a JSON-compatible value. Completion messages include task identity,
executor index, status, and timing. Exceptions become TaskError values with
remote traceback details. Keep process creation behind a main guard.

## Resource-controlled execution

```powershell
python -m workframe.launcher --cpu-percent 25 --memory-mb 512 --timeout 120 --report reports/run.json driver.py
```

The CPU cap and committed-memory budget cover the driver and its descendants
together. Timing covers startup through process-tree shutdown. Windows Job
Objects enforce the limits; unsupported assignment produces an error rather
than silently running without limits. `workframe-run` exposes the same launcher.

A reusable JSON profile can supply cpu_percent, memory_mb, and timeout. See
profiles/development.json and the generic examples in examples/.

## Configuration and diagnostics

ExecutionOptions configures input queue capacity, receive/shutdown deadlines,
message size, entry point, and working directory. Runtime.inspect() returns a
snapshot; export_diagnostics() writes JSON and JSONL observations. EventLog,
Counters, Stopwatch, and bounded timing samples support application diagnostics.

Scheduling policy and workload interpretation belong to the calling application.
For API usage, development commands, report interpretation, and troubleshooting,
see [CONTRIBUTING.md](CONTRIBUTING.md).
