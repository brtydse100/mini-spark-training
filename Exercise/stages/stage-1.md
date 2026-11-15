# Stage 1 - Build a working query engine

**Time:** 3 working days, then a mentor review. Use Python 3.11+ on Windows. Work without AI; documentation, debuggers, and profilers are allowed.

**Goal:** Write an application that reads a CSV table, filters its rows, counts matches, and displays matching rows using multiple executor processes.

## 1. Understand what you are building

Your **driver** is the application that accepts a query, assigns tasks to executors, collects their results, and produces the answer. An **executor** is a separate process running your task code.

Workframe provides process creation, JSON task/result transport, timing, and resource controls. You implement the table/schema handling, query methods, task logic, scheduling decisions, and result formatting. There is no ready-made query engine to call.

Install from the package index supplied by your mentor:

```powershell
python -m pip install workframe==0.4.0
```

See the [Workframe usage example](https://github.com/brtydse100/mini-spark-training/blob/main/Package/README.md#run-a-task) for starting processes and submitting a task. Repository: [mini-spark-training](https://github.com/brtydse100/mini-spark-training).

## 2. Read a table using its schema

Use the supplied `samples/single` and `samples/multiple` data folders. Each describes the same table: 1,200 rows stored in one file or four files. Each folder has an external `schema.json`.

- Support a table defined by one CSV file or a collection of CSV files and its schema.
- Use the declared CSV settings and column types. Fields arrive as text; implement conversion and validation. Do not count headers.
- Preserve quoted commas, quotes, Unicode, and multiline fields. The schema's `\N` token means null; empty text is different.
- Document comparison rules, case sensitivity, null behavior, decimal representation, and how invalid values/unknown columns are reported.

## 3. Execute your own tasks

First make one task count the data rows in one file. Then use the driver to distribute file tasks across several executors and combine their results.

A task is your Python file with a `run(data)` function. The driver submits its path and JSON-compatible input through Workframe; `run` returns a JSON-compatible value. Workframe carries that value back in a completion message with task identity. Read that message to obtain the result.

Keep process startup behind `if __name__ == "__main__":`. Track task identities, handle errors, and close executors after success or failure. Whole-file tasks are enough at this stage; a single file does not yet need splitting across executors.

## 4. Implement filter, count, and show

Provide query methods in your application. Choose your own calling syntax; this illustrates the required behavior:

```python
people = engine.table(files, schema="schema.json")
people.count()                         # 1200
people.filter(name_equals_alice).count()  # 300
people.filter(name_equals_alice).show(5)  # at most 5 matching rows
```

Here `name_equals_alice` stands for an expression you define, not supplied code.

- `filter` selects rows using your expression logic inside executor tasks.
- `count` combines executor partial counts into one integer answer.
- `show(n)` obtains bounded row results from executors and displays up to n matches with column headers. This is your application's method; implement its formatting after decoding results. Document output ordering.

Support comparisons (`=`, `!=`, `<`, `<=`, `>`, `>=`), grouped AND/OR/NOT, ranges, membership, null checks, text contains/prefix/suffix/LIKE, length checks, and basic numeric expressions (`+`, `-`, `*`, `/`). Document supported operand types and LIKE wildcard behavior. You choose the expression format; parsing SQL text is not required. Lazy execution is introduced in stage 2.

## 5. Measure and bring to review

Run the driver through Workframe's built-in timer and shared resource manager:

```powershell
python -m workframe.launcher --cpu-percent 25 --memory-mb 512 --timeout 120 driver.py
```

These limits are examples; use the budget your mentor assigns. The driver and all executors share it. Record elapsed time, CPU time, and peak committed memory. The launcher prints a summary; `Runtime.resource_usage()` / `ResourceMonitor` also provide in-memory observations. No report file is required.

Bring:

- Your code, run command, documented query/comparison rules, and resource measurements.
- Demonstrations on both file layouts: total count 1,200, Alice count 300, filtered show, no matches, nulls, multiline fields, and understandable invalid-input errors. Demonstrate each supported expression family.
- An editable **architecture.drawio** showing your chosen application components, driver/executor process boundaries, CSV/schema inputs, JSON task/results, and count/show output. Trace one query through it and keep it consistent with your code.

**Ready for stage 2:** your results are correct on both layouts, show respects its limit, executors shut down cleanly, and you can explain the design. Verify behavior yourself; an automated test suite is optional.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
