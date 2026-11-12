# Set up the Desktop copy

Open PowerShell. Use the actual Desktop path reported by Windows:

```powershell
$exercise = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Mini Spark Exercise'
Set-Location (Join-Path $exercise 'Package')
../Exercise/setup.ps1
./scripts/check.ps1
```

If your folder has a date suffix, change the folder name in the first command. Python 3.11+ must be installed. Setup creates a fresh .venv and installs the editable package and development dependencies. Initial dependency installation uses the network; all workbook/query execution is local. Excel itself is not required.

Expected check: two generic tasks return 6 and 9; the resource-managed run reports success. This verifies installation and the simple path, not advanced correctness.

If PowerShell blocks scripts, use these equivalent commands instead:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
./.venv/Scripts/python.exe -m pip install -r ../Exercise/requirements.txt
./.venv/Scripts/python.exe tools/smoke.py
./.venv/Scripts/python.exe -m workframe.launcher examples/local_driver.py
```

## Sample data

Already included under Exercise/data/samples:

- single/schema.json and single/part-001.xlsx
- multiple/schema.json and multiple/part-001.xlsx through part-004.xlsx

Both tables contain the same 1,200 records. Worksheet name is data. Read schema.json for column names, types, and nullability. Do not count the header. The age >= 18 then age < 30 checkpoint produces **200** rows in either table.

Generate a separate larger workload in a fresh directory:

```powershell
./.venv/Scripts/python.exe ../Exercise/tools/make_data.py ../Exercise/data/larger --rows 200000 --parts 8 --skew
```

## Built-in timer and resource manager

```powershell
./.venv/Scripts/python.exe -m workframe.launcher --profile profiles/development.json --report reports/example.json examples/diagnostics_driver.py
```

The profile gives the entire driver/process tree 25% of machine CPU capacity, 512 MiB committed memory, and a 120-second timeout. These are development examples; calibrate assessment settings on your machine. Extra executors share the same budget. The timer covers startup, computation, output, and shutdown. Reports contain timing, CPU, Windows memory counters, and actual limit readback. This measures committed memory, not physical RAM.

Exercise/starter/driver.py initially raises NotImplementedError. This is intentional; run the example for setup verification, then let trainees implement their driver.

## Rebuild the Python package

```powershell
./scripts/build.ps1       # Create wheel and source archive.
./scripts/test-wheel.ps1  # Build/install/test the wheel in isolation.
```

Wheel and source archives appear in Package/dist. Editable installation already picks up source changes in newly started processes; it does not require rebuilding after every edit.

## Instructor checks on this Desktop copy

From Package:

```powershell
./.venv/Scripts/python.exe -m pytest '../Instructor Guide/Verification' -q
```

Expected starter result: 20 passed and 4 xfailed. The expected failures document intentional bugs. Instructor conftest points at this Desktop copy, not the original scratch workspace.

## Reference count

```powershell
./.venv/Scripts/python.exe '../Instructor Guide/Reference/instructor/reference.py' ../Exercise/data/samples/single
./.venv/Scripts/python.exe '../Instructor Guide/Reference/instructor/reference.py' ../Exercise/data/samples/multiple --expression '../Instructor Guide/Reference/instructor/checkpoint.json'
```

Expected: 1,200 unfiltered; 200 for the two-filter checkpoint. Comparison rules are explicit in the oracle. Adapt assessment to a trainee's documented choices where the assignment permits them.

Workframe is installed as the ordinary distribution `workframe` (import `workframe`). Package dependencies cover the runtime only; Exercise/requirements.txt adds the Excel reader for the assignment. Workframe itself does not load table schemas or describe the exercise.


## Source checks versus wheel checks

From Package, scripts/check.ps1 exercises the current editable source install.
scripts/test-wheel.ps1 builds a fresh wheel, installs it into a temporary clean
environment, confirms the import comes from that environment, and runs public
checks plus the resource-managed example. The new wheel stays in Package/dist;
results stay in Package/reports. No manual wheel installation is required.
This validates the supplied ordinary execution checks; it does not prove that
all advanced behaviors or the trainee's query engine are correct.
