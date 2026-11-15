# Part 2 - Partitioning and lazy evaluation

**Time:** 5 working days, followed by a final review. Continue with your existing engine and the assigned total CPU/memory budget.

## 1. Partition and distribute the data

- Handle uneven files and tables larger than the memory budget.
- Divide work into bounded tasks, keeping executors productive without excessive scheduling overhead.
- Preserve logical CSV records: quoted fields can contain commas, quotes, Unicode, and line breaks. Do not lose or duplicate rows, or count headers.
- Keep outstanding tasks, input buffers, and result buffers bounded. Choose an executor count and partition size based on measurements.

## 2. Add lazy evaluation

- Let query methods describe operations without processing table records immediately.
- Trigger execution when count or show is requested.
- Allow queries to be reused or branched without unintentionally changing another query's definition.

## 3. Complete the checkpoint

Using syntax of your own design, apply age >= 18, then age < 30, then count.

- Constructing the query must not scan records or dispatch processing tasks.
- Execute both filters during one processing pass; do not materialize the full first result and scan it again.
- Verify the same result for one-file and multi-file tables, different partition sizes, and repeated executions.
- Show the filtered rows through show while respecting its display limit.

## 4. Measure and explain

- Record logical rows read, submitted tasks, and processing counters as well as elapsed time, CPU time, and memory. A final count alone does not prove one-pass execution.
- Include input reading and partition preparation in the measurements.
- Compare with your part-one implementation and explain the effect of partition size and executor count.
- Bring correct results, measurement evidence, and a clear explanation of your responsibilities and design decisions to the final review.

- Create **workframe-internals.drawio** explaining the package itself: the relevant modules/functions, process boundaries, task submission, execution, result/error collection, lifecycle, and resource observation/enforcement. Trace one real task through it and bring the editable file to review.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
