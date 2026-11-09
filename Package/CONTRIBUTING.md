# Developing Workframe

## Environment

Use Python 3.11+ and PowerShell from the project directory. The Windows launcher
requires Windows 10/11 and pywin32. Ordinary process execution uses Python's
spawn multiprocessing context.

```powershell
./scripts/setup.ps1
./scripts/check.ps1
```

Setup creates .venv and installs Workframe in editable mode with build and test
dependencies. Initial dependency installation needs network access. Execution
and diagnostics use local processes and files.

If script execution is restricted, use the equivalent commands:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
./.venv/Scripts/python.exe tools/smoke.py
./.venv/Scripts/python.exe -m workframe.launcher examples/local_driver.py
```

Activation is optional when using the explicit .venv interpreter. Source edits
apply to newly started processes. Restart existing executors after edits.

## Runtime API

Runtime(executors, options=...) owns executor processes. Use its context manager
or call start() and close(). Executor indices are zero based. The driver chooses
where and when to submit work.

- submit(executor, script, data, task_id=None) submits a task and returns its ID.
- receive(timeout=None) waits for a completion or raises TaskError/TimeoutError.
- receive_many(count, timeout=None) waits for a fixed number of completions under
  a shared receive deadline.
- submit_many(executor, tasks, limit=1) submits task dictionaries with script,
  data, and optional task_id fields to a selected executor.
- pending() exposes runtime pending state.
- inspect() returns executor status, counters, options, and timing observations.
- export_diagnostics(report_path, events_path=None) writes observations to files.

Task files define run(data), unless ExecutionOptions selects a different entry
point. Files are loaded for each execution. Do not depend on their module globals
persisting between executions. Imports use the normal Python environment; use
installed modules or self-contained task files.

A completion can arrive in a different order from submission. Success messages
contain task_id, executor, status, result, and metrics. TaskError.message contains
the corresponding failure envelope; remote_traceback exposes its traceback.
Inputs and outputs must serialize as JSON. Convert Decimal, dates, and custom
objects explicitly. NaN and infinity are rejected.

## Options and observation

```python
from workframe import ExecutionOptions, Runtime

options = ExecutionOptions(queue_capacity=2, event_capacity=100,
                           receive_timeout=30, max_message_bytes=8 * 1024 * 1024)
options.save("reports/options.json")
# Restore with ExecutionOptions.load(path).
```

Queue capacity bounds each executor input queue. The application remains
responsible for upstream buffering and submission policy. EventLog retains a
bounded ring of scalar metadata. Task timing measures each executor process;
job accounting separately measures the whole application tree.

inspect_task(path) from workframe.loading checks the syntax of a top-level
entry point without executing the file in the driver. Imports and actual
execution occur in the executor.

## Launcher and reports

```powershell
./.venv/Scripts/python.exe -m workframe.launcher --profile profiles/development.json --label trial-1 --report reports/trial-1.json examples/diagnostics_driver.py
./.venv/Scripts/python.exe -m workframe.launcher --profile profiles/development.json --label trial-2 --report reports/trial-2.json examples/diagnostics_driver.py
./.venv/Scripts/python.exe tools/summarize.py reports/trial-1.json reports/trial-2.json
```

The launcher creates the child suspended, assigns the Windows Job Object, then
resumes it. This captures interpreters spawned by virtual-environment redirectors.
CPU percentage describes machine scheduling capacity, not a core count. Memory
means aggregate committed virtual memory in MiB, not RSS or physical RAM.
Inherited OS restrictions can reduce the effective budget.

CPU caps throttle execution; memory caps reject allocations. A process can handle
an allocation failure and still exit successfully. Peak memory is the raw Windows
PeakJobMemoryUsed counter; it may exceed the configured budget following rejected
allocation attempts. Do not clamp this observation or treat it as sampled RSS.

Timeouts terminate the process tree. Descendants remaining after driver exit
produce orphan_processes and are terminated. Reports contain assigned and
read-back limits, environment metadata, elapsed time, CPU time, peak memory,
and process counts. This is resource-control tooling, not a security sandbox.
Summaries require matching budgets; callers control hardware and cache conditions.

## Test and build

```powershell
./.venv/Scripts/python.exe -m pytest tests -q
./scripts/build.ps1
```

The build creates dist/workframe-0.3.0-py3-none-any.whl and a source archive.
Verify the wheel in a separate environment:

```powershell
python -m venv .wheel-check
./.wheel-check/Scripts/python.exe -m pip install ./dist/workframe-0.3.0-py3-none-any.whl
./.wheel-check/Scripts/python.exe tools/smoke.py
```

Keep this checkout's examples for the smoke command. Continue source development
using the editable .venv install. Rebuilding is unnecessary for every source edit.

## Troubleshooting

- Imports: check `./.venv/Scripts/python.exe -m pip show workframe` and reinstall
  editable mode with the interpreter you actually use.
- Spawn bootstrap errors: put process creation behind the main guard.
- Missing results: use receive timeouts and inspect remote errors/executor status.
- Memory errors: include runtime, queues, inputs, outputs, and workers in the budget.
- Job assignment errors: inspect inherited Windows process restrictions. The
  launcher does not silently fall back to an unlimited run.
