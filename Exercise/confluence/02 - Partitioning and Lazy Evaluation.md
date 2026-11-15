# Stage 2 - Partition work and execute queries lazily

**Time:** 5 working days, then a final mentor review. Continue with your stage-one application and the same assigned total CPU/memory budget.

**Goal:** Handle uneven and large inputs efficiently, and run two chained filters in one pass when an action is requested.

## 1. Replace whole-file tasks with partitions

A **partition** is a bounded unit of table data assigned as one task. A file may contain many partitions; a partition is not necessarily a file.

- Make a large single-file table usable by multiple executors.
- Handle uneven file sizes and a table larger than the memory allowance.
- Distribute partitions so executors receive more work as they finish. Aim to reduce idle time; equal row counts do not guarantee equal processing time.
- Bound pending tasks, input buffers, and returned results. Creating more executors must not bypass the shared budget.
- Preserve every logical CSV record exactly once, including quoted multiline fields. Do not count headers or split a record at an embedded newline.

Choose your partition representation, size, and scheduling policy. Explain your choice using measurements, including input reading and partition preparation. Ask your mentor for the larger/uneven assessment data if it has not been supplied; the small samples establish correctness, not scalability.

## 2. Make queries lazy and reusable

**Lazy** means that defining a query records what to do without processing table rows yet. `count` and `show` are **actions**: they trigger execution.

The following is illustrative syntax, not a supplied interface:

```python
people = engine.table(files, schema="schema.json")
adults = people.filter(age_at_least_18)
young_adults = adults.filter(age_below_30)
# No data rows processed and no processing tasks submitted above.
answer = young_adults.count()  # Execute now; sample answer: 200.
young_adults.show(5)           # Execute an action and display up to 5 rows.
```

Schema/file metadata may be inspected while defining the query; table records must not be scanned. Creating `young_adults` must not change `adults` or `people`. Repeated actions must remain correct. Caching is not required.

## 3. Complete the one-pass checkpoint

Run `age >= 18`, then `age < 30`, then `count` on both supplied layouts.

- The answer must be **200** in each layout, using your documented null rules.
- During count, apply both filters as each row is processed. Do not build the complete first filtered table and scan it again for the second filter.
- Read each logical source row once for this action. Include any source scans used to prepare partitions in that accounting.
- Show evidence: source-record reads, task submissions, and executor row-processing counters before query construction, after construction, and after count. Explain where the counters are collected. A correct answer or shorter elapsed time alone does not prove laziness or one-pass execution.

`show(5)` is a separate action and may stop early. It is not the evidence for the full-scan count checkpoint.

## 4. Check correctness and resource use

Demonstrate the checkpoint with different partition sizes and executor counts, both file layouts, and repeated actions. Also demonstrate independent query branches, empty results, multiline records, and the stage-one filter/show behavior.

Compare your stage-one and stage-two implementations on the same machine, input, query, and resource budget. Include startup, reading, partition preparation, execution, and shutdown. Record elapsed time, CPU time, peak memory, task count, and executor activity. Explain idle time and overhead; partitioning need not make the small sample faster.

## 5. Explain the package and bring to review

Create an editable **workframe-internals.drawio** about Workframe itself. Stage one's diagram describes your application; this diagram explains the package code used by it.

Show actual relevant module/function names and trace one task through process startup, submission, JSON transport, task-file execution, result/error collection, and shutdown. Include process boundaries, task-state ownership, and where resource observation and enforcement happen. Be ready to open the code locations shown and explain their behavior.

Bring your code/run command, partitioning decisions, one-pass counter evidence, timing/resource comparison, and diagram.

**Complete:** results remain correct, query construction is lazy, count satisfies the one-pass checkpoint, large/uneven work stays within the budget, and you can explain both your application and Workframe's execution flow. Automated tests are optional; demonstrated behavior is required.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
