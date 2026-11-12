# Stages and schedule

## Stage one: days 1-3

Trainees implement driver/executor behavior, query methods, schema application, filter, count, and show using the library. They handle one or multiple CSV files as a single table and choose/document conversion and comparison rules.

Required filter families: comparison to literals/compatible columns, AND/OR/NOT and grouping, ranges, membership, null checks, text contains/prefix/suffix/LIKE, string length checks, and basic numeric expressions. A SQL text parser is not required. The broad scope is ambitious for three days; pilot it before setting hard pass deadlines.

Executors receive JSON instructions including a Python task-file path and inputs. The task file defines run(data), or another explicitly configured entry point. Executors return JSON partial counts or bounded rows. The driver aggregates counts and formats show output. Whole-file tasks are acceptable initially.

## Day 4: first review and consolidation

Trace one task through both codebases, demonstrate results, explain type/schema choices, inspect JSON messages, and discuss design assumptions. Let them correct issues from review.

## Stage two: days 5-9

Introduce uneven larger CSV files. Implement bounded partitions, effective task distribution, and lazy evaluation. Constructing a query must not scan records or dispatch work. count and show trigger execution. Two filters on one column run during one data traversal; count verifies the full dataset.

Trainees encounter and repair library failures caused by advanced submission, repeated execution, and retained inputs. They reproduce and explain each problem, refactor the relevant internals, and preserve stage-one behavior.

## Day 10: final review

Demonstrate delayed execution, a one-pass two-filter count, correctness across layouts/partition sizes, repeated queries, clean shutdown, repairs, and measured resource use. Discuss alternatives and remaining limitations.

## Optional stage three

For early finishers, grouped processing with shuffle. Give it a workload that needs redistributing records or partial counts by key. This extension is outside the required two-week completion target.
