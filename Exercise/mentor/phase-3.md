# Stage 3 - Mentor answers and review (optional)

**Read with:** [trainee stage-three brief](../stages/stage-3.md). Start only after the core exercise passes. Unfinished stage three must not delay core completion.

**Successful outcome:** a lazy grouped-count query redistributes intermediate contributions and combines groups on executors under the assigned resource budget.

## 1. Understand an acceptable solution

For grouped counting, a map task can combine rows locally into key/count pairs. A consistent routing rule sends each key to its responsible reducer executor. That executor combines contributions, and the driver assembles finished groups.

```text
map partition:       local_counts[key] += 1
route contribution:  destination = stable_partition(key, reducer_count)
reduce destination:  grouped_count[key] += partial_count
driver:              assemble completed group outputs
```

Local combination reduces transfer versus sending every row. The driver may coordinate transfer; direct executor messages are not mandatory. Doing all group aggregation in the driver does not satisfy the distributed-grouping goal.

Key serialization, types, and null handling need explicit rules. Routing must be consistent across processes. Python's default string hash may differ between independently started interpreters; a deterministic digest of a canonical key is one acceptable alternative.

Aggregation maps, transfer queues, and returned results must fit the budget. High-cardinality inputs may need bounded batches or spill/merge. One popular key can still concentrate work. Ask for the limitation and their handling of the assessed workload; do not demand a production optimizer.

## 2. Run correctness checks

Use both supplied file layouts:

| Query | Expected result, ignoring group display order |
| --- | --- |
| Group all rows by country and count | IL:300, US:300, GB:300, DE:300 |
| Sum those group counts | 1,200 |
| Filter country=IL, then group by country | Only IL:300 |
| Filter to no matches, then group | No groups, following the declared empty-result format |

- [ ] Change partition size and executor/reducer counts; results remain identical.
- [ ] Trace contributions for one key spanning multiple partitions to one destination.
- [ ] Compare a small hand-calculated or sequential example with their result.
- [ ] Check that retry/replay, if supported, does not silently double-count contributions. Automatic retry support is not required.
- [ ] Use skewed and many-distinct-key input to inspect buffers/state under the budget.
- [ ] Construct the query without processing data, then execute; filters still work before grouping and shutdown remains clean.

## 3. Review grouped-processing.drawio and questions

Require an editable diagram matching the implementation:

- [ ] Source partitions and map-side partial aggregation.
- [ ] Key-to-executor routing rule, process boundaries, and message direction.
- [ ] Intermediate key/count buffers and who owns them.
- [ ] Reducer aggregation and finished group results collected by the driver.
- [ ] Points where skew/high cardinality create pressure.

Ask: ?Why does every contribution for a key meet at the same executor?? A good answer explains stable routing and canonical keys. Ask: ?What reduces transfer?? Expect local combination. Ask: ?What happens with one popular key or many unique keys?? Expect discussion of concentrated work versus growing state, backed by their measurements.

## 4. Check measurements and decide

Record the command, query, input, budget, time, CPU, and memory. Include redistribution and final combination in the timing. Inspect data movement and state ownership rather than accepting a label such as shuffle.

**Complete:** correct grouped answers, executor-owned group combination, consistent routing, bounded execution, and an explainable diagram. **Needs follow-up:** driver-only aggregation, inconsistent routing, missing/duplicate contributions, or unbounded state. Keep the assessment proportional to this optional extension.
