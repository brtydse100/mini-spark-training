# Where the files are

## Package: standalone Workframe library

- src/workframe: runtime source, about 1,200 lines in 14 modules.
- pyproject.toml: ordinary workframe distribution metadata.
- README.md and CONTRIBUTING.md: library usage and development instructions.
- examples: generic execution and diagnostics examples.
- tests: public normal-path library tests, with no defect spoilers.
- profiles: resource-budget examples.
- scripts: library setup, checks, and building.
- tools: smoke execution and report summaries.

No assignment, schema, CSV data, exercise dependencies, answers, or trainee
placeholder lives inside this folder. Internal source defects are preserved.

## Exercise: materials given to trainees

- README.md and setup.ps1: assignment overview and dependency setup.
- requirements.txt: currently no extra data-reading dependencies; CSV uses the standard library.
- stages/stage-one.md: initial assignment; release later briefs after review.
- starter/driver.py: placeholder for the trainee engine.
- DATA_FORMAT.md: CSV dialect, schema, nulls, and record-boundary rules.
- data/samples: local CSV files and external JSON schemas.
- tools/make_data.py: reproducible CSV generator.

Distribute Package and Exercise together, keeping their sibling paths, or let
trainees install Workframe as a dependency and adapt their application paths.

## Instructor Guide: keep private from trainees

- Numbered Markdown: purpose, setup, stages, solution approaches, defect map,
  assessment, and this folder map.
- Reference/instructor: sequential oracle, sample runtime repairs, and checkpoint.
- Verification: full author checks, including intended failure scenarios and
  checks that the library contains no assignment material.

The oracle and runtime repairs are support tools rather than a completed
parallel query engine. Trainees implement that engine themselves.
