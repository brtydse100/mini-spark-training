# Stage 3 - Optional grouped counting and shuffle

**For early finishers only.** Complete the first two stages first. This extension is outside the required two-week assessment.

**Goal:** Count rows by a column value, with executors combining contributions for each group.

## 1. Add a grouped-count query

Extend your query methods to express a grouped count. Choose your own syntax; for example:

```python
people.group_by("country").count()
# Sample result: {"IL": 300, "US": 300, "GB": 300, "DE": 300}
```

Define grouping-key types, null behavior, and the JSON result format. Existing filters must work before grouping. Query construction must remain lazy.

## 2. Redistribute and combine intermediate results

The same country may appear in many input partitions. Its contributions must reach an executor responsible for combining them.

- Produce intermediate key/count contributions from partitions.
- Choose a consistent rule assigning each key to a destination executor.
- Send contributions to their destinations, combine them there, and collect completed groups in the driver. This redistribution is the **shuffle**.
- Bound aggregation state and transfer buffers under the assigned resource budget. Explain how you handle many distinct keys and heavily uneven groups.

The driver may coordinate transfers; direct executor-to-executor communication is not required. Simply collecting all contributions and doing every group aggregation in the driver does not satisfy the distributed-grouping goal.

## 3. Demonstrate correctness

On the supplied sample, grouping by country must produce the four groups shown above, totaling 1,200. Filtering to country IL before grouping must produce only IL with count 300.

Check both file layouts, several partition/executor counts, empty results, and heavily uneven groups. Compare small examples against a sequential calculation. Explain why no contribution is lost or counted twice and why each key reaches the same destination across processes.

## 4. Bring to review

- Your grouped query, task inputs/results, run command, and timing/resource measurements.
- An explanation of routing, intermediate buffering, aggregation ownership, and observed tradeoffs.
- An editable **grouped-processing.drawio** tracing partitions, intermediate key/count messages, destination executors, and final results, with process boundaries.

**Complete:** grouped answers are correct, combination happens across executors, execution remains lazy and bounded, and you can explain the data movement in your code and diagram.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
