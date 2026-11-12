# CSV tables and external schemas

A logical table consists of one or more .csv files and one schema.json in the
same directory. All files share column names, order, and types. Each file has
its own header record, which is never counted as data. single and multiple in
data/samples contain the same 1,200 rows in one and four files respectively.

## Physical format

The generated schema's csv object declares:

```json
{
  "encoding": "utf-8",
  "delimiter": ",",
  "quotechar": "\"",
  "null_token": "\\N"
}
```

Open files with the declared encoding and newline="". Use csv.reader or
csv.DictReader. CSV quoting protects embedded commas and line breaks; an
embedded quote is doubled. Do not parse with split(",") or assume one physical
line equals one logical row. The generator includes quoted commas, quotes,
Unicode, and multiline text specifically to exercise these cases.

## Types and missing values

The columns array declares each column's name, type, and nullable flag. The
schema is explicit: do not infer it from CSV text or Excel display behavior.
Convert field strings according to the declared type before comparing values.

Sample types: string, integer, decimal, boolean. Numeric text uses a decimal
point. Boolean fields use lowercase true/false. The reserved token \N denotes
null; ordinary empty text remains an empty string. Nullable applies to the null
marker, not automatically to empty text. Thus empty text in a numeric column
requires an explicit conversion/error policy; it is not inherently zero/null.
The literal string \N is reserved in this version of the data contract.

Document conversion, precision, null comparison, and invalid-value rules in
your engine. The instructor oracle uses strict integer conversion, Decimal,
exact lowercase boolean spellings, and SQL-style unknown for null comparisons.
Where the assignment permits different rules, make them explicit before review.

## Verification and partitioning

The standard sample contains 1,200 data rows in either layout. Applying age >= 18
and age < 30 yields 200 rows. Do not count headers or duplicate records when
partitioning. Count logical records processed as well as bytes/tasks to support
your one-pass claim. Keep parsing and partition preparation inside the budget.

The generator refuses to overwrite existing table directories. Generate larger
workloads in a fresh output path. CSV has no worksheet row limit; sizes are
bounded by available storage and the assigned execution resources.
