# How to solve stage two

## Partitioning

Treat worksheet rows as records. XLSX is not a flat line file; cutting raw workbook bytes is not a partitioning strategy. One viable design uses a streaming reader that makes bounded row batches, serializes those batches into JSON tasks, and distributes them to executors. A limited number of in-flight batches provides backpressure. Account for driver reading/serialization within the same CPU/memory budget.

Alternatively, design workbook/row-range assignments, but measure repeated workbook parsing. Reopening and walking from the start for every range can defeat the optimization. Whichever approach is chosen, every record must be processed exactly once and headers must not recur as data.

Balanced work does not require identical row counts. Variable row sizes or expensive predicates can make equal counts unequal costs. Measure task durations, try different chunk sizes, and choose an executor count instead of spawning as many as possible.

## Lazy evaluation

filter builds a query description, rather than scanning the table immediately. count/show materializes a plan into executable tasks. Each derived query should have independent immutable operation descriptions; branching a plan must not accidentally change another query.

For:

```python
q = table.filter(age >= 18).filter(age < 30)
answer = q.count()
```

The syntax is illustrative. The executor's row loop applies both predicates before counting:

```text
for each row in this partition:
    if first_condition(row) and second_condition(row):
        local_count += 1
```

This avoids writing a complete intermediate filtered table and reading it again. Count results from every partition are added exactly once. Both layouts in the supplied sample produce 200 for this query.

## Proving the behavior

Count records read, tasks created, and predicate processing. Construct the plan and demonstrate that those counters do not move. Trigger count and show processing. Measure all partition planning and input reading; do not hide a preprocessing scan outside the timer. A faster result alone does not prove lazy or one-pass execution.

show may stop before traversing the whole table, so retain count as the full-scan checkpoint. Test repeated actions and different partition sizes.

## Repair the underlying library

The new task patterns reveal tracking, stale-result, retained-input, and type-contract issues. See 06 - Bugs and Repairs.md. Establish a small reproduction before changing code. Separate responsibilities where that makes the root cause visible. Preserve JSON contracts, task errors, and shutdown. Fix the library rather than replacing it wholesale with Spark or another execution framework.

The supplied FixedRuntime illustrates repairs to the selected faults. It is not a full scheduler, complete query engine, or ready-made bounded pipeline; trainees still implement those decisions.
