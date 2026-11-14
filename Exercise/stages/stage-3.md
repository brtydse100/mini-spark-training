# Part 3 - Optional grouped processing

**Optional extension for early finishers.** Complete the first two parts before starting. This extension is outside the required two-week assessment.

Add grouped counting across the CSV table, for example counting people by country.

## 1. Describe grouped work

- Add a grouped-count operation to your application's query methods.
- Define grouping-key behavior, null handling, and the result format.
- Keep query construction lazy and execution within the assigned resource budget.

## 2. Implement redistribution

- Assign responsibility for groups to executors using a consistent routing rule.
- Redistribute intermediate key/count data so contributions to the same group meet at the responsible executor. This redistribution is the shuffle.
- Reduce data transfer with partial counts where appropriate, and bound intermediate buffers.

## 3. Combine and verify

- Combine grouped results without missing or duplicating contributions.
- Verify results across multiple input files, partition sizes, and executor counts, including empty input and heavily uneven groups.
- Compare with a simple sequential calculation and explain how your routing affects work distribution, communication, and memory.

## 4. Present your approach

- Demonstrate one grouped query and its JSON task/results.
- Explain your partitioning, redistribution, and result-combination responsibilities.
- Report timing and resource use, and discuss the tradeoffs you observed.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
