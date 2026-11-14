# Supplied CSV tables

samples/single and samples/multiple contain identical tables: 1,200 data rows
in one and four UTF-8 CSV files, with one external schema.json per table.

Each file starts with column names. Do not count the header as data. The schema
provides delimiter, quote character, null token, column types, and nullability.
Use csv.reader with the declared encoding and newline="". Quoted fields can
contain commas, doubled quotes, Unicode, and line breaks; a physical newline
is not necessarily a record boundary.

All parsed fields begin as text. Convert them according to the explicit schema.
The reserved token \N represents null, while an empty string remains empty text.
Boolean samples use true/false. Decimal values use a decimal point. Document
comparison, conversion, invalid-value, and missing-value behavior in your engine.

The combined conditions age >= 18 and age < 30 select 200 rows in either layout.
