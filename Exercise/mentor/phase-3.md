# Stage 3 - Mentor guide: AI-assisted engine and UI

**Read with:** [stage-three brief](../stages/stage-3.md). **Time:** one working week including reviews, after stages one, 1.5, and two. Claude is allowed here; earlier stages remain without AI.

**Successful outcome:** the trainee owns the architecture, directs Claude's implementation, and demonstrates correct distributed aggregation plus a live local monitoring UI. Both features need their own plan -> review -> build -> review cycle.

## 1. Run the review cycle twice

Use stage-3-plan.md with separate aggregation/UI sections and stage-3-architecture.drawio. Review the initial plan before asking for generated implementation. The trainee authors the design; assess their decisions and understanding rather than the volume of code or prompts.

| Checkpoint | Mentor action | Evidence needed to advance |
| --- | --- | --- |
| Plan | Read requirements, architecture, responsibilities, interfaces/messages, memory ownership, failure behavior, verification approach | A design specific enough to guide implementation; unresolved decisions made explicit |
| Plan review | Challenge bottlenecks and contracts; agree on acceptance cases | Recorded decision and required changes before building that feature |
| Build with Claude | Inspect selected changes and their verification; discuss significant architectural changes before implementation | Trainee understands generated code and keeps design/current behavior aligned |
| Implementation review | Run agreed cases, inspect code/diagram, resolve findings | Correct behavior, bounded resources, explainable tradeoffs and review outcomes |

Apply this to Feature A and Feature B separately, even if the overall architecture connects them. Schedule mentor availability early so reviews do not block the week. Keep a few examples of AI suggestions the trainee corrected/rejected; a full chat archive is unnecessary. Automated tests remain optional; convincing behavioral checks are mandatory.

## 2. Feature A: acceptable aggregation design

A valid design maps each source partition to partial aggregate states, routes keys consistently to reducer executors, merges their states there, and returns completed groups to the driver. Filters execute before grouping and query creation remains lazy.

```text
per key: count rows, sum numeric values, track non-null numeric count
route:   stable_partition(canonical_key, reducer_count)
merge:   add compatible partial states at the responsible executor
finish:  average = merged_sum / merged_non_null_count
```

Count rows and count non-null numeric values have different meanings; require explicit documented null behavior. Do not average partition averages without their weights. Define decimal precision and JSON encoding. Stable routing must work across spawned interpreters; Python's default string hash is not a dependable cross-process routing contract.

The driver may coordinate transfers but must not perform every group's aggregation. Require bounded queues, maps, and final collection. When intermediate state exceeds the in-memory allowance, spill/merge must preserve correctness and temporary files must be removed on success/failure. A spill implementation whose merge reloads all data at once is insufficient.

### Aggregation plan review

Ask who owns each key, what crosses each boundary, how average merges, what triggers spill, how merge stays bounded, and what happens on errors. Review key/type/null/precision contracts and acceptance cases before implementation.

### Aggregation implementation review

Run both supplied layouts: grouped country counts must be IL:300, US:300, GB:300, DE:300; their sum is 1,200. Filtering country=IL before grouping yields only IL:300. Verify sample sum/average against an independent sequential calculation using the same declared numeric rules.

Also use a small explicit fixture: country A with salary values 10, 20, 90; country B with salary 8. Expected A: count 3, sum 120, average 40; B: count 1, sum 8, average 8. Put A's 10/20 in one partition and 90 in another to expose unweighted averaging (52.5 is wrong).

Check empty results, documented null handling, changing partition/executor counts, keys spanning partitions, skew, and enough unique keys to force spilling under the budget. Inspect transfer/state bounds, cleanup after a task error, and regressions in stage-two laziness/filter/count/show. Executor recovery is a stretch goal, not a pass requirement.

## 3. Feature B: acceptable live monitoring design

One acceptable design emits bounded execution events, maintains job/task/executor state in a backend, and serves snapshots or updates to the browser. Polling and streaming are both acceptable. The UI must be driven by actual execution, not fabricated timer progress.

Events/snapshots need identities and consistent status transitions. Ask how event ordering, duplicate updates, slow consumers, reconnects, and bounded retention are handled. A strategy may coalesce intermediate measurements, but must preserve or reconcile final outcomes. Do not require a particular web framework or transport.

### UI plan review

Confirm the design covers all required views:

- Queries/jobs: identity, description, status, duration, progress.
- Execution plan: operations/dependencies and shuffle boundaries.
- Tasks/partitions: status, executor, duration, rows processed, errors.
- Executors: alive/busy/idle, completed tasks, available CPU/memory samples.
- Shared resources: assigned limits, elapsed time, aggregate observations.

Define an action as a job and distinguish processing steps from exercise stage numbers. For progress with unknown total work, show known counts/indeterminate progress until the total is known. Do not accept an invented percentage.

Ask where each measurement comes from and its scope. Missing per-executor measurements may be marked unavailable; process-tree totals must not be repeated as though each executor consumed them independently. Include UI backend/event work in the same enforced aggregate budget and bound history/buffers. Browser closure must not control query correctness.

### UI implementation review

- [ ] Run a sufficiently long query; watch statuses/progress change before completion and inspect final details.
- [ ] Reconcile displayed completed tasks and aggregate row counts with engine evidence, using their documented counter semantics across execution steps.
- [ ] Show operation dependencies and where shuffle occurs.
- [ ] Run uneven work and use durations/assignment to identify slow or idle executors.
- [ ] Make a task raise; display the failed task/job and useful error matching the engine. Recovery is not required.
- [ ] Close/reconnect the browser while execution continues; results stay correct and current/final state becomes visible again.
- [ ] Run multiple jobs or a slow viewer; retention and update queues stay bounded within the stated policy.
- [ ] Compare the same query/data/budget with monitoring enabled/disabled and explain overhead. Confirm enforcement includes the UI backend.

A resource monitor supplies samples; it does not prove one-pass execution or enforce limits. Keep the launcher and application counters in the verification story.

## 4. Review diagrams, AI use, and completion

The editable stage-3-architecture.drawio must cover aggregation flow/ownership, shuffle/spill, execution events, monitoring state, UI updates, process boundaries, resource scope, and failure paths. Ask the trainee to trace one query and one failure through both the picture and generated code.

Ask them to explain a design choice Claude challenged, a suggestion they rejected/corrected, and how they verified it. Choose a generated function and ask about its inputs, ownership, failure cases, and callers. Accept reasoned design revisions rather than insisting the first design remain unchanged.

**Complete:** both features passed plan and implementation reviews; aggregation and spill are correct/bounded; UI reflects real execution; earlier behavior still works; the trainee owns and explains the implementation. **Needs another review:** code they cannot explain, missing review checkpoints, fabricated/stale UI state, driver-only grouping, wrong averages, or unbounded state. Record concrete findings and follow-up evidence. Pilot the one-week target; visual polish and recovery should not displace these core requirements.
