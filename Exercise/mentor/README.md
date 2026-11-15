# Mentor guide

These pages contain answers and review instructions. Give trainees the stage briefs and data; keep these notes for mentors. Reviews run on the trainee's computer using their application. No separate setup or private verification scripts are needed.

| Review | Trainee brief | Mentor answers | Diagram to bring |
| --- | --- | --- | --- |
| Stage 1: working queries | [Stage 1](../stages/stage-1.md) | [Stage 1 guide](phase-1.md) | architecture.drawio |
| Part 1.5: package walkthrough | [Part 1.5](../stages/stage-1.5.md) | [Part 1.5 guide](phase-1.5.md) | workframe-internals.drawio |
| Stage 2: partitioning and laziness | [Stage 2](../stages/stage-2.md) | [Stage 2 guide](phase-2.md) | Update the part-1.5 diagram as needed |
| Stage 3: AI-assisted aggregation and UI | [Stage 3](../stages/stage-3.md) | [Stage 3 guide](phase-3.md) | stage-3-architecture.drawio |

## Before the exercise

1. Supply the configured package-index details, Workframe version, CSV data, schemas, and trainee pages. No application starter is required.
2. Assign one total CPU/memory budget and timeout for the driver and every descendant process together. Record the machine and settings used for comparisons.
3. Prepare a stage-two assessment corpus: one large file, uneven multi-file input, and enough data to exceed the assigned memory allowance if fully loaded. Preserve schema/CSV validity. Establish expected results before assessment; the supplied 1,200-row samples alone cannot establish scalability.
4. Schedule three working days for stage one, then one review day including part 1.5 (half to one day); stage two gets five days plus one review day. Stage three adds five days including its reviews: roughly three weeks overall. Calibrate through a pilot, especially expression breadth and spilling/UI scope.
5. Keep stages one, 1.5, and two without AI. In stage three, trainees author the architecture and use Claude to generate implementation after mentor plan approval. Reserve separate plan and implementation reviews for aggregation and for the UI.
6. Prepare small known-result sum/average cases, a high-cardinality spill workload, uneven tasks, and a controlled task-error scenario for stage three. Use the same shared budget for the engine and UI backend.

## Run each review

Ask for the code/version, run command, comparison rules, measurements, and editable draw.io file. Follow the phase page in order: trace the design, run correctness checks, inspect resource/processing evidence, then discuss tradeoffs. Verify behavior before comparing speed.

Use the trainee's syntax and declared rules. Do not require a particular class hierarchy, SQL parser, or automated test suite. Ask them to predict a result before running a check and explain any discrepancy. Accept different designs that satisfy the requirements.

Review diagrams against actual code, process boundaries, and message flow. An image export may accompany the editable .drawio file but does not replace it. A polished picture without an explainable execution trace is insufficient.

## Interpret measurements correctly

The package's Windows launcher enforces the shared CPU/committed-memory budget and prints timing/accounting results. ResourceMonitor and Runtime.resource_usage() expose sampled in-memory observations; these can miss short-lived processes or allocation spikes and do not enforce limits. Report files are optional. Neither source proves how many CSV rows were read: stage two needs application-level counters.

## Record the decision

- **Ready:** required behavior and explanations are demonstrated.
- **Ready with follow-up:** required behavior works; record a small documentation/design improvement with an owner and review point.
- **Needs another review:** correctness, required execution behavior, resource compliance, or understanding is missing. Record the failing case and the evidence needed next time.

Use a short record: stage, code version, input/budget, observed results, diagram trace, decision, and follow-up. Stage three is now part of the exercise; only recovery is a stretch task. Record its two plan reviews and two implementation reviews in stage-3-plan.md, with the final integrated demonstration.
