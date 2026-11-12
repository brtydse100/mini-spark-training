# Assessment and review

Use a common machine and an assigned CPU/memory profile. All driver/executor processes share one budget. More processes do not buy more capacity. The timer includes startup, processing, result output, and shutdown. Choose final dataset sizes and completion targets through a pilot; supplied limits are development examples.

Check correctness before ranking speed. Compare multiple repeats and report a median, while keeping CSV data, query, environment, resource budget, and cache conditions consistent. The launcher reads back enforced Windows limits. Memory is committed memory; the raw Windows peak counter can include effects of rejected allocations and is not physical RAM.

## Stage-one review prompts

- Explain how schema values and filter expressions become executable tasks.
- Trace one JSON task/result through both codebases.
- Demonstrate count and show, single- and multi-file equivalence, empty results, and errors.
- Explain ownership of driver, executor, schema, parser, and evaluator logic.

## Stage-two review prompts

- Prove constructing a query does no data processing.
- Prove both filters run in one pass and counts do not depend on partition size.
- Explain backpressure, workload balance, and executor-count choice.
- Reproduce each selected library defect and explain the faulty assumption and repair.
- Show that simple stage-one execution still works.
- Justify targeted cleanup and identify reliable modules left alone.

Assessment dimensions: understanding, correctness/verification, responsibility boundaries/maintainability, and measured performance reasoning. A fast wrong answer fails. A blanket rewrite without understanding is not the intended outcome. Automated test authoring is optional, but behavioral evidence is required.

Optional early-finisher work: implement grouped aggregation with shuffle. Keep it out of the required pass criteria.
