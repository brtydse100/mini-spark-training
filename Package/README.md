# Workframe training exercise

Build a local Python processing engine over Excel tables. The provided package is generic execution plumbing; you implement the driver, executor tasks, schema handling, filter, count, and show.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), then [stage one](course/stage-one.md).

Windows 10/11, 64-bit Python 3.11 or newer. Everything runs locally after dependencies are installed. Microsoft Excel is not needed at runtime.

```powershell
./scripts/setup.ps1
./scripts/check.ps1
./.venv/Scripts/python.exe tools/make_data.py data/stage-one --rows 1200 --parts 4
```

Each generated table directory contains one shared schema.json and one or more .xlsx workbooks. single and multiple represent identical rows. Workbooks use the data worksheet and literal cells, with column names in the first row.

Use the supplied runtime primitives to build your own engine. The small sum example demonstrates task-file loading and JSON transport only. The starter is exercise material: understand its behavior before extending it. Passing the installation smoke check establishes only the ordinary example path.

## Assessed execution

```powershell
./.venv/Scripts/python.exe -m workframe.launcher --cpu-percent 25 --memory-mb 512 --timeout 120 --report reports/my-run.json trainee/driver.py
```

Replace trainee/driver.py with your implementation. It initially raises NotImplementedError. CPU and committed-memory limits cover the driver and all executors together. More processes do not receive additional resources. Values above are development examples; the mentor sets assessed limits. The timer includes startup, execution, output, and shutdown. Review the JSON report even on failure.

The learner implements filter, count, show, and later partitioning and lazy evaluation. No completed table/query engine is included in the package.


The library source is in src/workframe (14 modules). ExecutionOptions,
runtime snapshots, bounded events and task timing, task-file inspection,
and reusable benchmark profiles are provided as generic support primitives.
Try examples/diagnostics_driver.py under profiles/development.json. The
trainee remains responsible for all query and scheduling logic.
