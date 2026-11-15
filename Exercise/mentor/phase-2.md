# Phase 2: answers and mentor checks

## Intended outcome

The application handles larger uneven input through bounded partitions and
effective work distribution. Query construction is lazy. Both filters in a
chain run during one processing traversal. The trainee can explain the package
internals they depend on, not just the application's interface.

## A sound solution

A valid approach streams logical CSV records into bounded batches, submits a
limited number of tasks, and replenishes work as executors finish. Keep pending
input, active work, and returned batches bounded. A byte-range design is also
valid if record boundaries, headers, encoding, and ownership are correct.
Never assume every newline ends a record or every equal-row partition has equal
cost. Include parsing, boundary discovery, and serialization in the budget.

Query methods produce independent operation descriptions. An action compiles
that description into tasks; building a plan does not consume source records.
A branch must not mutate another query's operations.

```text
query = source + [age >= 18, age < 30]       # describe only
on count:
    for each bounded partition:
        process each row once:
            convert according to schema
            if first_condition(row) and second_condition(row):
                increment this partition's count
    combine partition counts exactly once
```

There must be no complete intermediate table after the first filter. show runs
the same predicates but can stop at its documented limit. Retain count as the
full-scan checkpoint because show alone may inspect only a prefix.

## What to look for in workframe-internals.drawio

Require the diagram to reflect the package version/code actually used. Relevant
components should carry real module/function names; group supporting modules
where listing every helper would add noise.

- [ ] Runtime construction/start, ExecutionOptions, and process creation.
- [ ] submit/submit_task, TaskSpec where used, _do, and input queues.
- [ ] JSON encode/decode and the driver/executor process boundary.
- [ ] worker.work -> _pack -> loading.load -> task-file run(data).
- [ ] Success/error message creation, result queue, receive, and TaskError.
- [ ] Pending/completed task state, identities, and who owns retained data.
- [ ] close, sentinels, joins, and fallback process termination.
- [ ] ResourceMonitor/process_tree observation versus launcher/resources.Job
  enforcement/accounting; these have different roles and measurement scope.
- [ ] A complete traced task, with message direction and data lifetime.

Ask the trainee to follow a real task through the diagram and open the named
code locations. A generic Spark picture or a copy of their stage-one application
architecture is not sufficient. Observed behavior and assumptions should be
distinguishable. The diagram should make the package's execution model clear.

## Mentor-only package problems and answers

The trainee-facing requirements intentionally do not tell them to modify the
package. Assess their diagnosis when new workloads expose a problem. Do not
force an inefficient application design just to trigger a particular path; use
a focused reproduction if their valid architecture avoids it naturally.

- **Task tracking:** Runtime._do stores _x[executor] = task_id. Two submissions to
  one executor before receiving overwrite the first identity. Receiving the first
  result raises a mismatch. Track task identity independently with executor
  ownership, validate the returning pair, and remove that exact active task.
- **Stale results:** _done is consulted solely by ID at submission. Execute an ID
  with input producing 1, then reuse the completed ID with input producing 9;
  the starter can return 1 again. Remove implicit reuse or define explicit valid
  cache/identity semantics; an ID alone is not a content-aware query cache.
- **Retained input:** _history retains each serialized payload. Long sequential
  runs grow retained memory despite bounded in-flight work. Release input after
  ownership ends and retain only bounded diagnostic metadata. Reference release,
  not immediate OS RSS reduction, is the key evidence.
- **Type contracts:** settings.amount can return int, float, or str; pending and
  empty batch results also vary in type. Normalize semantic capacities under a
  clear contract, reject invalid/fractional values as appropriate, and return
  consistent empty shapes. Do not coerce all user task data indiscriminately.
- **Structure:** the long _do function mixes several responsibilities. Look for
  targeted improvements that make ownership and transitions comprehensible,
  while recognizing working modules that need no changes.

Useful repair criteria are task/result association, repeated-execution
correctness, bounded ownership, clear accepted input types, preserved JSON/error
contracts, and clean lifecycle behavior. No single reference architecture is
mandatory, and replacing the entire dependency with another engine misses the
learning objective.

## Cases to demonstrate

- [ ] age >= 18 then age < 30 gives 200 in both supplied file layouts.
- [ ] Constructing/branching a query does not move source-record/task counters.
- [ ] count executes both predicates in one source-processing pass.
- [ ] Different partition sizes and executor counts preserve results.
- [ ] Multiline/Unicode CSV records are not split, lost, duplicated, or counted as headers.
- [ ] Repeated actions and changed inputs do not return stale answers.
- [ ] Long runs stay bounded in queued inputs, retained data, and results.
- [ ] show respects its limit without collecting the entire filtered dataset.
- [ ] Stage-one cases still work; errors and shutdown remain understandable.
- [ ] Their diagram explains the code and the behavior they demonstrated.

Ask for application-level record/task instrumentation. The resource monitor
cannot by itself prove how often CSV records were parsed. Do not accept only a
final count or a faster timer reading as proof of lazy, one-pass execution.

Advance when correctness, lazy semantics, bounded resource use, and package
understanding are demonstrated together. Discuss timing on the same machine,
query, data, and budget, including preprocessing and cache conditions. Ask what
was changed, why that layer owns it, and what tradeoff remains.
