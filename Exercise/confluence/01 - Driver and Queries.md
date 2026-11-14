# Part 1 - Driver, executors, and queries

**Time:** 3 working days, followed by a review. **Environment:** Python 3.11+, Windows. Work without AI; documentation, debuggers, and profilers are allowed.

Build a local query engine over CSV tables using Workframe. A table can occupy one file or several files, with one external schema.json describing its columns and types.

## 1. Prepare your environment

- Create a virtual environment and install the provided Workframe wheel:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install ./workframe-0.3.0-py3-none-any.whl
./.venv/Scripts/python.exe -c "from importlib.metadata import version; print(version('workframe'))"
```

- Locate the supplied CSV tables and schema.json files. Read the CSV encoding, quoting, and null-marker rules. Use Python's csv module for record parsing.

## 2. Create your driver and executor tasks

- Create several executors through Workframe and distribute tasks from your driver.
- Send JSON instructions identifying a Python task file and its input. Each task file exposes run(data) and returns JSON-compatible results.
- Track completed tasks, collect results, report errors, and shut down cleanly.

## 3. Implement your query methods

- Apply the explicit schema and document conversion, missing-value, and comparison rules.
- Implement filter, count, and show in your own application. show formats decoded executor row results with column headers; it is not a Workframe method.
- Support comparisons, AND/OR/NOT and grouping, ranges, membership, null checks, text contains/prefix/suffix/LIKE, length checks, and basic numeric expressions. A SQL text parser is not required.
- Return partial counts for count and bounded row batches for show. Support one-file and multi-file tables. Whole-file tasks are acceptable initially.

## 4. Demonstrate your result

- Show correct counts and displayed rows, including empty results, quoted multiline fields, nulls, and invalid inputs. Do not count headers.
- Run through the built-in timer and shared resource manager:

```powershell
./.venv/Scripts/python.exe -m workframe.launcher --cpu-percent 25 --memory-mb 512 --timeout 120 --report reports/run.json driver.py
```

- Use the assigned budget; these values are examples. The driver and all executors share one CPU/memory allowance. Record elapsed time, CPU time, and peak committed memory.
- Bring your run command, results, and a task-flow explanation to the review. Verify behavior; writing automated tests is optional.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
