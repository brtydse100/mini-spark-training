# Mentor review guide

Use these notes during reviews; give trainees the stage briefs and Confluence
pages rather than this folder. These are answer guides and manual review
checklists, not another setup process or private verification program.

- [Phase 1: application architecture and queries](phase-1.md)
- [Phase 2: partitioning, lazy execution, and the package](phase-2.md)
- [Phase 3: optional grouped processing](phase-3.md)

## Review method

1. Ask the trainee to demonstrate their own application on their machine.
2. Inspect their editable draw.io file and trace a real execution through it.
3. Replay selected cases using their commands and documented comparison rules.
4. Ask them to explain evidence and tradeoffs before suggesting a change.
5. Record the result as ready, ready with follow-up, or needs another review,
   with concrete observations and next actions.

Do not prescribe a class hierarchy or judge by the number of patterns used.
Accept different sound designs. Verify correctness before comparing speed. The
initial three-day phase and overall ten-day target should be calibrated through
a pilot, especially with the broad filter-expression scope.

## Diagram deliverables

- Phase 1: architecture.drawio, showing the application design they chose.
- Phase 2: workframe-internals.drawio, explaining package internals and a task's
  full execution flow with process, message, and ownership boundaries.
- Phase 3, if attempted: grouped-processing.drawio, showing redistribution by key.

Require an editable .drawio file. An exported image may accompany it but does
not replace the source. Review content against the actual code, not appearance.
There is no single reference diagram to copy.

ResourceMonitor and Runtime.resource_usage() expose in-memory observations.
Sampled peaks can miss short-lived allocations/processes. Windows Job Object
accounting/enforcement covers the shared assessed budget; report files are
optional. No resource allowance is added by creating extra executors.
