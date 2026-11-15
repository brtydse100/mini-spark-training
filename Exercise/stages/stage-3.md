# Stage 3 - Design and build with Claude

**Time:** one full working week, including reviews. Complete stages one, 1.5, and two first. This is the third week of the exercise. Claude is allowed in this stage; the earlier parts remain without AI.

**Goal:** extend your engine with distributed aggregation and a live local monitoring UI. You own the architecture and verification; Claude helps generate the implementation.

## 1. Follow the cycle for each major feature

Complete this cycle separately for aggregation and the monitoring UI:

1. **Plan:** write your design before asking Claude to generate implementation code. Describe responsibilities, interfaces/JSON messages, data flow, memory ownership, failure behavior, and how you will verify it. Include an editable draw.io architecture. You author and explain the decisions.
2. **Review:** present the plan to your mentor. Agree on acceptance checks and resolve design issues before building that feature.
3. **Build:** direct Claude in manageable tasks. Review generated changes, check behavior, and keep the design current. Bring significant architectural changes back for review before implementing them.
4. **Review:** demonstrate the feature and its checks, trace the generated code, explain tradeoffs, and address findings before closing the feature.

Use one short **stage-3-plan.md** with a section for each feature and an editable **stage-3-architecture.drawio** covering both. Record review decisions, significant changes, and a few examples of suggestions you corrected or rejected. You do not need to submit every chat message.

## 2. Feature A: distributed aggregation

Add grouped count, sum, and average to your lazy query methods. For example, using syntax of your own design:

```python
people.group_by("country").count()
# {"IL": 300, "US": 300, "GB": 300, "DE": 300} on the sample
people.filter(adult_condition).group_by("country").sum("salary")
people.group_by("country").average("salary")
```

- Apply filters before grouping. Document key types, null handling, empty results, and numeric precision.
- Redistribute intermediate contributions so the executor responsible for a key combines all its contributions. This redistribution is the shuffle. The driver may coordinate transfers; it must not do every group's aggregation itself.
- Keep aggregation state, pending transfers, and results bounded. Support intermediate data larger than the allowed in-memory state, using disk spilling/merging when necessary. Clean up temporary files on completion or failure.
- Demonstrate both supplied layouts, different partition/executor counts, empty results, skewed keys, and many distinct keys. Compare small cases with a sequential calculation.

## 3. Feature B: live local monitoring UI

Build a browser UI for your running engine, inspired by [Spark UI](https://spark.apache.org/docs/3.5.7/web-ui.html). Choose your UI tools. It must display real execution data, not simulated progress.

| View | Required information |
| --- | --- |
| Queries/jobs | Identity, description, running/completed/failed status, duration, task progress |
| Execution plan | Operations, dependencies, and shuffle boundaries |
| Tasks/partitions | Status, executor assignment, duration, rows processed, error details |
| Executors | Alive/busy/idle state, completed tasks, available CPU/memory observations |
| Shared resources | Assigned CPU/memory limits, elapsed time, aggregate CPU/memory observations |

An action such as count/show starts a job. Execution-plan steps are processing steps, not the numbered parts of this exercise.

- Update the UI while a query runs and retain its final status/details for review within a documented bounded history.
- Design how execution events become UI state. Keep event queues, history, and refresh work bounded. Missing measurements must be shown as unavailable; distinguish per-executor samples from shared totals.
- Display a task failure accurately and preserve a useful error. Automatic executor recovery is a stretch task, not required.
- Keep execution correct if the browser is closed or reconnects. Run the UI backend and engine under the same aggregate resource allowance; include monitoring overhead in measurements.

## 4. Final integrated review

Bring your code/run commands, plan with review outcomes, editable diagram, correctness evidence, and resource measurements. Automated tests are optional; demonstrated verification is required.

Run a query long enough to observe progress, then use the UI to identify uneven work. Run a task that fails and explain its state/error from UI to engine code. Demonstrate that aggregation results remain correct and execution stays bounded with monitoring enabled. Compare elapsed time/resources with monitoring disabled using the same query/data/budget.

**Complete:** both features passed their plan and implementation reviews, grouped results are correct, the UI reflects real execution, resource usage stays bounded, and you can explain and take responsibility for the Claude-generated code.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
