# Windows development guide

## Setup

Install 64-bit Python 3.11+ with its launcher/PATH option, then run commands from this folder in PowerShell. Use `python --version` to confirm the interpreter. Windows 10/11 is the supported assessment environment.

```powershell
./scripts/setup.ps1
./scripts/check.ps1
```

The scripts create .venv and install this package in editable mode, plus pywin32, openpyxl, pytest, and build. Network is needed for initial dependency installation; data and execution are local. If your machine policy blocks scripts, run the equivalent commands below in the terminal; no permanent policy change is necessary.

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
./.venv/Scripts/python.exe tools/smoke.py
./.venv/Scripts/python.exe -m workframe.launcher examples/local_driver.py
```

Always use the .venv interpreter. No activation is required. Source edits under src/workframe take effect on the next new process. Restart existing executors after an edit. Rebuilding is only necessary to verify distribution/install behavior.

## Execution primitives

```python
from pathlib import Path
from workframe import Runtime

if __name__ == "__main__":
    with Runtime(2) as runtime:
        runtime.submit(0, Path("my_task.py"), {"input": 10}, task_id="one")
        message = runtime.receive(timeout=30)
        print(message["result"])
```

A task file defines `run(data)` and returns JSON-compatible data. Files execute locally as Python code. Paths are resolved by the driver before dispatch. Imports resolve from the normal Python environment; use installed modules or self-contained task files. Runtime uses Windows-compatible spawn. Put process creation behind the main guard. A task file is loaded for each execution; do not depend on its module globals persisting across tasks.

`Runtime(executors).start()` starts processes; the context manager calls start and close automatically. Executor indices are zero based. `submit(executor, script, data, task_id=None)` returns an ID; a missing ID is generated. `receive(timeout)` returns a completion envelope or raises TaskError/TimeoutError. Completion order can differ from submission order. `submit_many(executor, tasks, limit=1)` accepts task dictionaries with script/data/optional task_id; inspect implementation behavior before relying on new execution patterns. `pending()` exposes runtime state. Public method details are intentionally sparse in places as part of the exercise; installation and build instructions are dependable.

Success envelope: `{"task_id":"one","executor":0,"status":"ok","result":10}`. Errors include task identity, exception type/message, and traceback in TaskError.message. No HTTP calls are involved. Transport uses actual JSON serialization; Decimal/date/custom objects need explicit representation, and NaN/infinity are rejected.

## Data and schema

```powershell
./.venv/Scripts/python.exe tools/make_data.py data/small --rows 1200 --parts 4
```

The generator refuses to overwrite an existing table directory. Choose a fresh output path to regenerate. Each table has schema.json with table, version, sheet, and columns (name, type, nullable). Types in the sample are string, integer, decimal, and boolean. Excel numeric cells may already be numeric; salary is stored as decimal text deliberately. Apply the explicit schema consistently. openpyxl does not apply the external JSON schema for you.

Read .xlsx with openpyxl; implement table/query semantics yourself. Never count the header as data. Both single-workbook and multiple-workbook tables must work. Do not implement XML/ZIP decoding. Formula calculation, macros, formatting, and merged cells are outside the dataset contract. Reading .xlsx does not require Microsoft Excel or cloud services.

## Timing and resource reports

`python -m workframe.launcher [options] driver.py [driver arguments]` creates the child suspended, assigns the Windows job, then resumes it. This also captures child interpreters spawned by Windows virtual-environment redirectors. CPU is a percentage of the machine's total scheduling capacity, not a core count. Memory is aggregate committed virtual memory in MiB, not working-set/RSS memory. Parent OS restrictions may make the effective budget lower. Unsupported job assignment is an error; the launcher never silently falls back to an unlimited run.

Reports include status, driver exit code when available, elapsed_seconds, cpu_seconds, peak_job_committed_bytes, total_processes, and assigned limits. CPU caps throttle execution; memory caps reject allocations. A handled allocation failure can still produce a successful process exit. Status alone does not prove that no memory request was rejected. The peak is the raw Windows PeakJobMemoryUsed counter; in our allocation-rejection experiment it exceeded the configured limit despite the allocation failing. Do not clamp the measurement or interpret it as sampled physical RAM.

Timeouts terminate the job. A driver that exits while descendants remain produces orphan_processes and those processes are terminated. Use context managers and join your own children. The launcher observer stays outside the budget and does no query work. It is assessment tooling, not a security sandbox. Use a common machine and benchmark profile for fair comparison.

## Build and verify a wheel

```powershell
./scripts/build.ps1
python -m venv .wheel-check
./.wheel-check/Scripts/python.exe -m pip install ./dist/workframe_training-0.2.0-py3-none-any.whl
./.wheel-check/Scripts/python.exe tools/smoke.py
```

The wheel contains the generic library, not datasets or the assignment solution. Keep the source checkout/examples while running the last command. After verifying a wheel, continue development using .venv, whose editable install follows source changes.

## Troubleshooting

- Import errors: check `./.venv/Scripts/python.exe -m pip show workframe-training` and reinstall editable mode.
- Spawn bootstrap errors: move driver execution under `if __name__ == "__main__"`.
- Excel file locked: close readers/workbooks before rewriting; use fresh output directories.
- Allocation errors: inspect the complete application budget including Python, readers, queues, and workers.
- No result: use receive timeouts, inspect TaskError.message and worker exits, and reduce to a small reproduction.
- Job assignment error: run in an ordinary Windows terminal and inspect inherited process restrictions. Do not remove assessed resource limits to claim a passing benchmark.


## Execution options and observation

```python
from workframe import ExecutionOptions, Runtime

options = ExecutionOptions(queue_capacity=2, event_capacity=100,
                           receive_timeout=30, max_message_bytes=8 * 1024 * 1024)
options.save("reports/options.json")
# Load the same settings with ExecutionOptions.load(path).
# Within your driver, use Runtime(2, options=options).
```

queue_capacity bounds each process input queue. It is a primitive, not an
application scheduler or a guarantee that upstream work construction is
bounded. You still design submission policy and result handling.

Runtime.inspect() provides executor PIDs/liveness, counters, options, and a
bounded window of task timings. Runtime.export_diagnostics(report, events)
writes a JSON snapshot and optional JSONL event history. EventLog stores
metadata only. These observations are separate from whole-job CPU/memory
accounting. Task results now include metrics for elapsed/process-CPU time.
Use examples/diagnostics_driver.py to inspect the ordinary path.

```powershell
./.venv/Scripts/python.exe -m workframe.launcher --profile profiles/development.json --label trial-1 --report reports/trial-1.json examples/diagnostics_driver.py
./.venv/Scripts/python.exe -m workframe.launcher --profile profiles/development.json --label trial-2 --report reports/trial-2.json examples/diagnostics_driver.py
./.venv/Scripts/python.exe tools/summarize.py reports/trial-1.json reports/trial-2.json
```

Profiles set the CPU percentage, committed-memory MiB, and timeout together.
Explicit CLI values override a development profile. The mentor controls the
assessed command/profile. Reports include the actual Windows limit readback
and machine/interpreter metadata. Summaries reject mixed budgets and count
failed runs separately; they cannot establish correctness or equal hardware.

Task-file entrypoints default to run; ExecutionOptions.entrypoint can select
another callable. inspect_task(path) in workframe.loading checks a top-level
function's syntax without running it in the driver. Actual import/execution
still happens inside the executor. Keep process creation behind a main guard.
