# How to solve stage one

This is an architectural solution guide, not the only acceptable class design.

## Responsibilities

- Table: records workbook paths and explicit schema; validates headers.
- Schema: converts/validates cell values according to declared types.
- Expressions: represent columns, literals, operators, and grouped conditions.
- Driver: creates executors/tasks, tracks task identity, receives results, and aggregates them.
- Executor task file: reads its assigned input, applies schema and predicates, and returns a JSON-compatible result.

## Processing flow

1. Resolve a file or table directory into workbook paths and one schema.
2. Read the designated worksheet with openpyxl, preferably streaming rows.
3. Check headers against the schema and exclude the header from records.
4. Convert each value; keep null, boolean, integer, decimal, and string semantics explicit.
5. Evaluate the filter expression against each row.
6. For count, increment a local integer. For show, collect only a bounded result batch.
7. Return a JSON result with task identity. The driver adds partial counts or formats rows with headers.

Initially assign one whole-workbook task per executor at a time. When a task completes, the trainee driver can choose more work. A table in one workbook can use one executor in stage one; splitting it is stage two.

## Expressions over JSON

An example representation is:

```json
{"op":"ge","args":[{"column":"age"},18]}
```

AND/OR nodes hold other expressions. A column node resolves a row value; literal nodes supply values; an operator evaluates its arguments. A callable alone is not a JSON query representation. The exact syntax of the trainee's public methods is their decision.

Use an evaluator/interpreter for this expression tree. Keep evaluation separate from orchestration. The instructor oracle in Reference/instructor/reference.py demonstrates one sequential implementation; do not distribute it as starter code.

## Type rules

The JSON schema is authoritative. Decide whether numeric text is converted, whether non-integral values can be integer columns, how incompatible comparisons fail, how empty text differs from null, and how decimals are represented over JSON. Do not silently truncate 28.5 into 28. A Decimal value needs a JSON-compatible representation. The oracle uses Decimal internally and SQL-like unknown for null comparisons, but permitted trainee choices must be documented before grading them.

## Show

show is a method of the trainee's own Table/Query abstraction, not a method
added to the Workframe library. Executors return JSON-compatible row data;
Runtime.receive() returns a decoded dictionary. The driver extracts and combines
bounded row results, then the application formats them. A formatting helper may
accept those results, but the query action remains application-owned. A JSON
dictionary itself does not have a show method.

Use a limit, such as show(20), and a documented ordering guarantee. Task results carry bounded rows rather than the entire filtered table. The driver coordinates limits and may read more than the displayed number because of concurrency. It must still bound memory. Do not assume completion order is table order.

## Verification

Compare one-workbook and multi-workbook answers. Check zero matches, nulls, quoted/newline text inside cells, boolean combinations, invalid columns/types, and the header. The sample has 1,200 rows. Trace actual JSON messages. Use the supplied launcher to measure a complete run under the shared budget.
