# Mini Spark Training

## Repository layout

- [Package](Package/README.md): Workframe, a standalone Python library with source,
  examples, public tests, resource monitoring, and CI package builds.
- **Exercise/data**: supplied CSV tables and external schema.json files.
- **Exercise/confluence**: three concise pages to copy into Confluence.
- **Exercise/stages**: complete briefs for stages [1](Exercise/stages/stage-1.md),
  [2](Exercise/stages/stage-2.md), and optional [3](Exercise/stages/stage-3.md).

No separate instructor-guide folder, private verification suite, application
starter, or exercise setup scripts are required.

## Starting the exercise

Give trainees the pages, CSV data/schema, and the session's package index details:

```powershell
python -m pip install workframe==0.4.0
```

The command assumes your package index is configured; this repository does not
publish to public PyPI automatically. Trainees write their own application.
The first Confluence page includes the existing GitHub repository URL.

Workframe exposes elapsed time, CPU, and process-tree memory directly in memory
through ResourceMonitor and Runtime.resource_usage(). No report file is required.
The built-in Windows launcher enforces the shared CPU/committed-memory budget
and can optionally save a report when --report is provided.

## Package artifacts and checks

The Build Python package workflow runs on pull requests, main, and manual
requests. It tests the normal library interface, builds source/wheel artifacts,
verifies an installed wheel in a clean environment, and provides downloads.
PR builds get development versions. You manage registry publication.

Library tests can run on a developer/trainee machine or in CI. They are normal
package tests rather than a separate instructor tool collection.
