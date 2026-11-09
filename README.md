# Mini Spark Training

A two-week local Python exercise for developers familiar with OOP and SOLID.
Trainees build an Excel query engine on a deliberately flawed generic process
execution skeleton, then extend it with partitioning and lazy evaluation.

## Start here

- [Start here](START%20HERE.md): the folder layout.
- [Instructor guide](Instructor%20Guide/00%20-%20START%20HERE.md): purpose, setup, stages, solution approaches, defects, and assessment.
- [Setup instructions](Instructor%20Guide/02%20-%20Setup.md): Windows installation and verification.
- [Package](Package/README.md): the material intended for trainees.
- [Stage one](Package/course/stage-one.md): initial assignment.

The instructor guide and reference repairs are instructor-only materials.
Distribute the Package folder to trainees rather than this whole repository.

## Contents

Package/src/workframe contains the execution skeleton (approximately 1,200 lines
across 14 modules). Package/data/samples includes equivalent single- and
multi-workbook Excel tables and external JSON schemas.

The skeleton includes a built-in timer and Windows Job Object enforcement of a
shared CPU and committed-memory budget for the driver and all executors. It also
contains intentional readability, contract, state, and execution defects.

## Quick start on Windows

From Package in PowerShell:

```powershell
./scripts/setup.ps1
./scripts/check.ps1
./.venv/Scripts/python.exe -m pytest '../Instructor Guide/Verification' -q
```

The instructor suite expects 18 passing checks and 4 strict expected failures
that reproduce the deliberately planted defects. Those expected failures are
part of the exercise. A completed trainee engine is not supplied.

Virtual environments, caches, runtime reports, build artifacts, and large
generated datasets are not tracked. Dependency installation needs network
access; table processing runs entirely locally. Pilot the schedule and calibrate
assessment budgets before setting time thresholds.
