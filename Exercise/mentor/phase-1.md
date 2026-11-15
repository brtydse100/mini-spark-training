# Stage 1 - Mentor answers and review

**Read with:** [trainee stage-one brief](../stages/stage-1.md). **Target:** three working days plus review.

**Successful outcome:** the trainee's driver uses Workframe executors to implement filter, count, and show over one-file and multi-file CSV tables with an external schema.

## 1. Understand an acceptable solution

Workframe owns process creation and JSON transport. The application owns source selection, schema conversion, expression evaluation, scheduling, result combination, and display. Look for clear ownership rather than a required number of classes.

A valid execution is:

1. The driver resolves files/schema and creates file tasks containing the requested operation and filter description.
2. Workframe starts executor processes and loads the trainee's Python task file.
3. Its run(data) reads logical CSV records with the declared settings, skips each header, applies null/type rules, and evaluates the filter.
4. For count it returns a partial integer; for show it returns a bounded JSON-compatible row result.
5. The driver associates completions with tasks, combines counts exactly once or formats rows with headers, and shuts down processes on success or failure.

```text
executor count task:
    matches = 0
    for each logical CSV record after its header:
        row = convert_using_schema(record)
        if expression_matches(row):
            matches += 1
    return matches

driver count action:
    return sum(each completed task's partial count exactly once)
```

A structured JSON expression tree is one acceptable way to represent comparisons and nested AND/OR/NOT. A SQL text parser is not required. Whole-file tasks and an eager implementation are acceptable here; do not demand stage-two partitioning or laziness. A single-file table need not use all executors yet, but multi-file execution must demonstrate multiple executor processes.

show belongs to the application, not Workframe or the result dictionary. Limit rows returned and collected; displaying five rows after collecting every match is insufficient. Accept a documented ordering policy rather than assuming completion order equals source order. Decimal values need an explicit JSON representation preserving their intended precision.

## 2. Run correctness checks

Ask the trainee to predict, then run these checks on both supplied layouts:

| Query | Expected result |
| --- | --- |
| Count all rows | 1,200 |
| name equals Alice | 300 |
| country in IL/US | 600 |
| active equals true | 800 |
| age is null | 71 |
| note is null | 110 |
| name equals a value absent from the table | 0 |

Then check behavior rather than only totals:

- [ ] show(5) displays at most five qualifying rows with headers; an empty result is well-formed. Explain its ordering and inspect how many rows are retained.
- [ ] Headers are excluded in every file. Quoted commas, doubled quotes, Unicode, and multiline fields stay intact.
- [ ] The reserved null marker differs from empty text. A valid header-only CSV returns count zero.
- [ ] Unknown columns and malformed typed values produce understandable errors. A failed executor task identifies its task and does not leave the run hanging.
- [ ] Start and finish several tasks, including tasks completing in a different order. Confirm results are associated correctly and processes close.

Cover each expression family from the brief using small, manually understandable rows. For example, with typed rows `(age=20, salary=10, name=Alice)` and `(age=35, salary=20, name=Bob)`: age >= 18 AND age < 30 selects only Alice; NOT(name = Alice) selects only Bob; salary * 2 >= 30 selects only Bob. Add membership, ranges, OR/grouping, contains/prefix/suffix/LIKE, and length checks. Check equality and comparison boundaries too. Use their documented case, wildcard, null, and invalid-operation rules; do not silently impose a different SQL dialect.

## 3. Review architecture.drawio and understanding

Require the editable file to match their code. Ask them to trace one filter/count request and then show through:

- [ ] Application components and responsibilities, separated from Workframe.
- [ ] Driver/executor process boundaries and transport direction.
- [ ] CSV/schema inputs, task-file path, JSON input, completion identity, and result.
- [ ] Conversion, filtering, aggregation/formatting, error handling, and shutdown.
- [ ] Where timing/resource observation and the shared budget apply.

Ask: ?Where does filtering run?? A good answer names the executor task and expression handling. Ask: ?What happens when tasks finish out of order?? A good answer explains identity-based collection. Ask: ?Why these responsibilities?? Look for reasons tied to changes they expect, not only pattern names.

## 4. Check resources and decide

Run their driver through the built-in launcher under the assigned aggregate budget. Record command, elapsed time, CPU time, and peak committed memory. Confirm measurements include the driver and executors; creating more executors gives no extra allowance. In-memory observations are useful, but do not replace enforcement.

**Ready:** correct filter/count/show, both layouts, explicit schema/comparison rules, bounded show results, controlled lifecycle/resources, and an explainable diagram. **Needs another review:** wrong counts, broken CSV records, collecting all show results, orphaned processes, or inability to explain their own execution. Missing automated tests alone is not a failure.
