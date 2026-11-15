# Stage 2 - Mentor answers and review

**Read with:** [trainee stage-two brief](../stages/stage-2.md). **Target:** five working days plus review, after [part 1.5](phase-1.5.md). Continue without AI.

**Successful outcome:** bounded partitions keep executors productive; queries are lazy and independent; the two-filter count makes one source pass; the trainee understands the package code their application uses.

## 1. Understand an acceptable solution

One valid design is a driver that streams logical CSV records into bounded batches, dispatches a bounded set of tasks, and replenishes work when executors finish. Executors convert/evaluate rows and return small partial counts or bounded show results. This is an example, not a required architecture.

Byte-range partitions are also possible, but quoted newlines and multibyte encoding require correct boundaries. A pre-scan to find boundaries is another source traversal: it must be included in one-pass accounting. Equal row counts need not mean equal cost. Look for measured task sizes and low idle time rather than perfectly equal worker totals.

Lazy query methods produce independent descriptions of operations. An action executes that description:

```text
people = source description
adults = people plus [age >= 18]
young = adults plus [age < 30]      # no row processing or dispatch yet

on young.count():
    stream source once into bounded partitions
    executor: convert each row; apply both predicates; count matches
    driver: sum each task result exactly once
```

There is no complete intermediate table between the filters. Creating young must not alter adults or people. Repeated actions must remain correct; caching is not required. show is a separate action that may stop early, so it cannot prove the full-scan checkpoint.

## 2. Run the lazy/one-pass checkpoint

Use the supplied samples first, with instrumentation that counts actual reads and processing rather than inferred totals:

| Review point | Expected evidence |
| --- | --- |
| Before and after constructing/branching queries | No increase in source data rows processed or processing tasks submitted; metadata reads are allowed |
| After count with age >= 18 then age < 30 | Answer 200 in each layout; 1,200 logical source records read once for that action, including partition-preparation scans |
| Inside executor processing | Both filters are applied in the same row-processing traversal; no second scan of a complete first-filter result |
| After constructing young from adults | adults still represents only age >= 18; people remains unfiltered |
| Repeated count / separate show(5) | Correct fresh action behavior; show displays at most five matches |

Counters from spawned processes need to reach the driver; reading only driver-local variables is insufficient. Ask where each counter increments and inspect the loop. If the second predicate short-circuits on rejected rows, its evaluation count may be lower; that is not evidence of missing rows. Reset or subtract counters per action.

Repeat with different partition sizes/executor counts and both file layouts. Run stage-one correctness/error checks again, especially multiline CSV, nulls, headers, empty results, and shutdown. A count of 200 alone does not prove the required execution behavior.

## 3. Review package failures and repairs (mentor only)

The trainee pages do not announce dependency defects. When a problem appears, ask for the failing input, expected/actual behavior, and a trace to the responsible layer before suggesting changes. These are selected starter-0.4.0 defects; compare against the version they actually use.

| Problem and focused reproduction | Cause in the starter | Acceptable repair direction |
| --- | --- | --- |
| Submit two tasks to one executor before receiving; first completion can raise an identity mismatch | Runtime._do replaces _x[executor] with the latest task ID | Track outstanding tasks and executor ownership independently; validate/remove the exact returning task |
| Complete an ID with input yielding 1, then reuse that ID with input yielding 9; old result can return | Submission consults _done using only the ID | Remove implicit reuse or define explicit valid identity/cache rules; an ID alone is not content-aware caching |
| Run many sequential tasks with substantial inputs; retained payloads grow despite bounded active work | _history keeps every serialized input | Release payload ownership when no longer needed; retain bounded diagnostics. Inspect retained references, not only immediate OS memory reduction |
| Use different limit forms or inspect empty results; type-dependent behavior appears | settings.amount returns int/float/str; pending varies by state; empty submit_many returns 0 rather than a list | Define/validate capacity types and consistent result shapes; reject fractional/invalid limits as appropriate |

For the type issue, ask them to compare limit=2, limit="2", limit=2.5, pending when empty/nonempty, and an empty batch. Do not normalize all task data to one type: user data legitimately contains different types.

The long _do function and weak names/docs make ownership hard to follow. Look for focused improvements to responsibilities, names, contracts, and explanation, while preserving working transport/error/lifecycle behavior. Do not demand a complete rewrite or a specific class hierarchy.

A correct application may avoid a particular faulty path. Do not force a poor scheduler just to trigger it; use a small reproduction during discussion. Judge diagnosis and a justified remedy. Ask what reproduces the defect, why the chosen layer owns the fix, and how they checked existing behavior afterward. Replacing Workframe with another engine misses the exercise's learning objective.

## 4. Revisit the part-1.5 package trace

The package diagram/code walkthrough was assessed in [part 1.5](phase-1.5.md). Reuse that file rather than assigning another diagram. Ask the trainee to update changed paths and trace the state/ownership affected by their stage-two work or repairs. Use the detailed part-1.5 checklist only where relevant to the changes.

## 5. Check scale/resources and decide

Use the prepared large and uneven inputs, including a single file using multiple executors and a corpus larger than the assigned memory allowance. Observe pending work, buffers, retained results, and executor activity over a long run. Bounded task count alone does not prove bounded retained memory.

Compare stage one and stage two on the same machine/input/query/budget, including startup, reading, partition preparation, execution, and shutdown. Record time, CPU, memory, task count, and idle activity. A small sample can get slower because of overhead; do not require an arbitrary speedup. The resource monitor cannot prove row-scan counts.

**Ready:** correct results, independent lazy plans, one-pass evidence, bounded large/uneven execution, and an explainable package diagram/code trace. **Needs another review:** eager record scans, hidden preprocessing passes, unbounded queues/history/results, stale answers, or unexplained package behavior. Automated tests are optional; behavioral evidence and justified changes are required. After passing, begin the AI-assisted stage three.
