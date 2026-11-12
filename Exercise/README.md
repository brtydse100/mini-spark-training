# Mini Spark exercise

This folder contains the assignment and table-processing materials. Workframe,
in the sibling Package folder, is the local execution dependency you will use.

From the repository root in PowerShell:

```powershell
./Exercise/setup.ps1
./Package/scripts/check.ps1
```

Read [stage one](stages/stage-one.md). Write your engine under starter/ or create
your own application directory. Table samples and schema.json files are under
data/samples; single and multiple contain equivalent rows. See [DATA_FORMAT.md](DATA_FORMAT.md) for parsing, types, and null handling. The library itself
contains no table/query implementation.

From Package, generate a fresh workload with:

```powershell
./.venv/Scripts/python.exe ../Exercise/tools/make_data.py ../Exercise/data/larger --rows 200000 --parts 8 --skew
```

Run your driver through the library's built-in timer and shared resource manager:

```powershell
./.venv/Scripts/python.exe -m workframe.launcher --profile profiles/development.json --report reports/run.json ../Exercise/starter/driver.py
```

The driver is initially unimplemented. Use Package/examples/local_driver.py for
installation verification. The mentor controls the assessed budget and releases
stage two after review. Keep the sibling Instructor Guide private from trainees.
