# Stage one: build the engine foundations

Budget: three implementation days, then mentor review/consolidation. Work without AI. You may use documentation, debugging, profiling, standard Python facilities, and openpyxl. Write and run your own experiments. Automated test authoring is optional; verifying behavior is required.

## Assignment

Implement a driver and executor task logic using workframe. A driver creates several executor processes. An executor receives JSON describing a Python task file and its inputs, executes the task's run(data), and returns JSON. You implement how table work becomes tasks and how results combine.

Support a table in one .xlsx file or spread across several files. All parts use one explicit external schema.json. Generate examples with tools/make_data.py. Column names live in the first worksheet row; its name comes from the schema. Ignore formatting, formula calculation, and macros.

Implement your own Python query methods:

- filter: comparisons, text searching, length checks, ranges, membership, null checks, numeric expressions, and grouped AND/OR/NOT conditions.
- count: number of data rows surviving the filters.
- show: display matching rows with column headers. Default limit 20 is recommended; document your limit and ordering guarantee.

Include comparison to literals and compatible columns, LIKE with documented percent/underscore wildcard and escape rules, and nested conditions. No SQL string parser, joins, window functions, or subqueries are required. Use ordinary expression/method definitions of your design. Do not delegate query processing to pandas, Spark, SQL engines, or an existing DataFrame library.

Define conversion/comparison rules: supported types, precision, invalid numeric text, non-integral integers, null versus empty text, case sensitivity, incompatible types, division by zero, and unknown columns. Document whether null comparisons use SQL-style unknown or another explicit model. Schema validation must cover all workbook parts.

Filter expressions need a representation that can be sent as JSON to executors. Count tasks should return partial counts; show tasks return bounded row results. Do not collect an entire filtered table to display twenty rows. Your application owns driver dispatch/aggregation, executor behavior, parsing, query representation, and error handling. Whole-file tasks are acceptable initially.

## Deliverables

One documented command runs your driver under the supplied timer/resource manager. Demonstrate count, filter, and show, single-file and multiple-file equivalence, zero matches, empty tables, invalid input, and clean shutdown. Show actual JSON tasks/results and report measured wall time, CPU time, and job memory. Limits cover the entire program, not each executor separately. Mentor-provided settings override development examples.

## Review

Trace one task through your engine and the dependency. Explain responsibilities, how schema/expressions cross the JSON boundary, how you verified answers, and one assumption that might fail with a different workload. Bring a small reproducible example. You are not expected to rewrite the entire library.
