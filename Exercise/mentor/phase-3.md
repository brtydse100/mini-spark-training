# Phase 3: optional grouped processing - answers and mentor checks

## Intended outcome

This is for early finishers; it is outside the required two-week pass criteria.
The trainee implements a grouped operation whose intermediate data must be
redistributed across executors, while preserving lazy execution and the budget.

## A sound solution

For grouped counting, a map task can build local key/count pairs instead of
sending every source row. Route each key consistently to its responsible
reducer/executor, combine all contributions there, and send completed grouped
results to the driver. This routing/transfer is the shuffle.

```text
map partition:       local_counts[key] += 1
route intermediate: destination = stable_partition(key, reducer_count)
reduce destination: grouped_count[key] += partial_count
driver:              assemble completed grouped outputs
```

The exact transport is a design choice. The driver can coordinate transfer;
direct worker messages are not mandatory. It must still redistribute ownership
of grouped work rather than collecting and aggregating everything centrally
while merely calling that shuffle.

Define key serialization/type/null rules consistently. Routing must be stable
across executor processes. Do not assume Python's default string hash produces
the same value in independently started interpreters. A deterministic digest
of a canonical key representation is one valid choice, not a required design.

Bound local aggregation maps and transfer buffers. If many distinct keys exceed
memory, batching or a documented spill strategy is needed for that workload.
A single popular key can still concentrate work; ask them to explain skew
rather than requiring a production optimizer.

## What to look for in grouped-processing.drawio

- [ ] Source partitions and map-side partial aggregation.
- [ ] Key-to-destination routing, with process and message boundaries.
- [ ] Intermediate key/count messages and their buffering/ownership.
- [ ] Reducer execution, grouped output, and final driver collection.
- [ ] Where skew or high cardinality creates pressure.

Require the editable file only if phase three is attempted. A timing or network
picture without the data-routing rule does not explain a shuffle.

## Cases and expected results

For unfiltered grouping by country on the supplied sample:

```json
{"IL": 300, "US": 300, "GB": 300, "DE": 300}
```

- [ ] One-file/multi-file layouts and partition/executor counts agree.
- [ ] Group counts sum to the filtered count (1,200 for the unfiltered sample).
- [ ] Empty input yields no groups or another explicitly documented empty result.
- [ ] Filter country=IL before grouping yields just IL:300; use it to discuss skew.
- [ ] Keys with zero contributions are not invented as source groups.
- [ ] Input/partial-result replay is not silently counted twice.
- [ ] Construction remains lazy, resources bounded, and shutdown clean.

Use a simple hand-calculated or sequential result for small cases; no private
verification program is needed. Ask why combining local counts reduces transfer,
how destinations are chosen, and how work changes when one key dominates.

Accept when correct distributed grouping, routing ownership, and bounded data
movement are explained and demonstrated. Keep this extension optional; do not
hold up a successful core exercise for unfinished advanced optimizations.
