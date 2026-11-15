# Mini Spark Training

## Repository layout

- [Package](Package/README.md): Workframe, a standalone Python library with source,
  examples, public tests, resource monitoring, and CI package builds.
- **Exercise/data**: supplied CSV tables and external schema.json files.
- **Exercise/confluence**: four trainee pages to copy into Confluence (1, 1.5, 2, 3).
- **Exercise/stages**: complete briefs for stages [1](Exercise/stages/stage-1.md),
  [1.5](Exercise/stages/stage-1.5.md), [2](Exercise/stages/stage-2.md), and
  [3](Exercise/stages/stage-3.md).

- [Exercise/mentor](Exercise/mentor/README.md): phase answers, diagram-review
  criteria, mentor questions, and manual acceptance checks. Keep these notes
  separate from the pages/data given to trainees.

No separate setup process, private verification suite, or application starter
is required. Mentors review demonstrations on the trainee's machine.

## Exercise progression

Plan for roughly three full-time weeks:

1. Build driver/executor filter, count, and show (three days plus application review).
2. Complete part 1.5: read Workframe and create its package diagram (within the first review day).
3. Add partitioning and lazy one-pass execution (five days plus review).
4. Use Claude to build distributed aggregation and a live local monitoring UI (five days including reviews).

Parts 1, 1.5, and 2 are without AI. In stage 3, trainees own the architecture and
follow plan -> mentor review -> build with Claude -> mentor review for each of
the two major features. The UI displays real job/task/executor/resource data.
Recovery is a stretch task; aggregation and monitoring are required.

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
