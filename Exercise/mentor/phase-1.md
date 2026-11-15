# Phase 1: answers and mentor checks

## Intended outcome

A working driver creates executors and implements filter, count, and show over
one or several CSV files sharing an external schema. Trainees implement the
application; Workframe supplies generic execution/transport facilities.

## A sound solution

Possible responsibilities are a table/input descriptor, schema converter,
expression representation/evaluator, driver, task implementation, and result
formatter. These need not be separate classes if another design has clear
ownership and can evolve.

The driver resolves sources and schema, creates tasks, submits work, tracks
identity, handles completions/errors, and closes executors. A whole-file task
is acceptable initially. A table in one file need not use all executors yet.

The executor task file exposes run(data). It opens CSV with the schema encoding
and newline="", validates/skips the header, interprets the reserved null token,
converts values, evaluates predicates, and returns JSON-compatible results.

```text
partial_count = 0
for each logical CSV record:
    row = apply_schema(record)
    if predicate(row):
        partial_count += 1
return partial_count
```

The driver sums partial counts exactly once by task identity. For show, return
bounded row batches and format them in the application with column headers.
The application's query.show() is not a Workframe method or a method on a JSON
dictionary. Completion order does not imply source order; require a documented
ordering policy and a display limit.

A structured expression such as a comparison node containing a column reference
and literal can be serialized to JSON and evaluated inside the task. Nested
AND/OR/NOT expressions provide composition. A SQL text parser is not required.

## What to look for in architecture.drawio

- [ ] The chosen application components and their actual responsibilities.
- [ ] A clear boundary between application code and Workframe.
- [ ] Driver and executor process boundaries; queues/transport where used.
- [ ] CSV files, schema, task Python files, JSON inputs, and returned results.
- [ ] A trace from query request to task execution to count/show output.
- [ ] Ownership of conversion, filtering, aggregation, errors, and shutdown.
- [ ] Where resource measurement and the shared budget apply.

Ask for the diagram early enough to discuss their intended architecture, then
require the review version to match the implementation. Do not demand specific
class names, a particular UML notation, or a diagram of every helper function.

## Cases to run on the trainee's application

For the supplied unmodified sample, both single and multiple layouts should give:

- [ ] Unfiltered count: 1,200; name equal to Alice: 300.
- [ ] Country in IL/US: 600; active equal to true: 800.
- [ ] Age is null: 71; note is null: 110.
- [ ] Count excluding headers; identical answers across file layouts.
- [ ] A nonexistent literal returns zero; show on no matches stays well-formed.
- [ ] show(n) returns at most n qualifying rows and includes headers.
- [ ] Quoted commas, quotes, Unicode, and embedded newlines remain in one field.
- [ ] Empty input with a valid header is handled according to their contract.
- [ ] Unknown columns and invalid values produce understandable errors.

Use equality/case/null examples consistently with the supplied schema and the
trainee's documented permitted rules. Empty text and the reserved null marker
must not be silently confused. Ask how decimals and non-JSON-native values are
represented without losing intended precision.

## Questions and review decision

Ask them to trace one JSON task/result through their diagram and code; explain
where an expression is evaluated; show how failures identify their task; and
explain what happens when workers finish in a different order.

Advance when count/filter/show are correct, schema and file layouts work,
executor lifecycle is controlled, resources respect the assigned budget, and
the trainee can explain the architecture. A wrong answer, unbounded collection
for show, missing cleanup, or an unexplained diagram needs follow-up. Writing
an automated test suite is optional; behavioral evidence is required.
