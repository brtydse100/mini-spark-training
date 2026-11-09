# Where the files are

## Package ? give this to trainees

- src/workframe: actual generic library source (about 1,200 lines in 14 modules).
- trainee/driver.py: placeholder for their application.
- examples: simple transport and diagnostics demonstrations, not a query solution.
- data/samples: ready-to-use Excel tables and external schemas.
- course/stage-one.md: initial assignment.
- profiles/development.json: example shared CPU/memory/timeout budget.
- scripts: setup.ps1, check.ps1, build.ps1.
- tools: data generator, smoke checks, and benchmark-report summarizer.
- CONTRIBUTING.md: detailed development/build reference.

## Instructor Guide ? keep this yourself

- 00 through 08 Markdown files: setup, purpose, stages, solution approaches, faults, assessment, and this map.
- Reference/instructor/reference.py: sequential correctness oracle.
- Reference/instructor/fixed_runtime.py: example repairs to runtime defects.
- Reference/instructor/checkpoint.json: two-filter checkpoint expression.
- Verification: author checks, including the deliberate failure scenarios.

There are no copied virtual environments, build caches, or old package versions in this Desktop copy. Run setup to create a new local editable environment. Python source changes in Package/src/workframe then affect newly launched workers.

The reference repair and oracle are support tools, not a complete solved parallel query engine. The required engine is the trainee's implementation.
