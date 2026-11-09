# Mini Spark Training

A two-week local Python exercise for developers familiar with OOP and SOLID.
Trainees build an Excel query engine using Workframe, then extend their engine
with partitioning and lazy evaluation while investigating dependency behavior.

## Folders

- [Package](Package/README.md): Workframe, a standalone local Python task library.
- [Exercise](Exercise/README.md): assignments, Excel data, JSON schemas, starter
  application, and data generator.
- [Instructor Guide](Instructor%20Guide/00%20-%20START%20HERE.md): solution
  approaches, defect map, reference tools, assessment, and private author checks.

Only the outer exercise materials describe the educational setup. The library
has ordinary project documentation, its own package metadata, examples, and
public tests. Do not distribute the Instructor Guide to trainees.

## Setup

From the repository root in PowerShell:

```powershell
./Exercise/setup.ps1
./Package/scripts/check.ps1
./Package/.venv/Scripts/python.exe -m pytest 'Instructor Guide/Verification' -q
```

The instructor checks expect 20 passing checks and four strict expected failures
that reproduce the planted defects. Workframe's own tests cover ordinary use;
the private checks capture the exercise-specific failure scenarios.

The built-in timer and Windows Job Object manager enforce one shared CPU and
committed-memory budget for the driver and its executors. Everything executes
locally after dependency installation. Pilot the schedule and calibrate limits
before assigning performance thresholds.
