"""Sequential assessment oracle; no parallel engine provided to trainees.

Expressions: {"column": "age"}, literal JSON values, or
{"op": "gt", "args": [{"column": "age"}, 18]}.
Null follows SQL-style unknown. Only True selects a row.
"""
import argparse
import csv
from decimal import Decimal
import json
from pathlib import Path
import re


def convert(value, kind):
    if value is None:
        return None
    if kind == "string":
        if not isinstance(value, str):
            raise ValueError("Expected text")
        return value
    if kind == "boolean":
        if type(value) is bool:
            return value
        if value in ("true", "false"):
            return value == "true"
        raise ValueError("Expected boolean")
    if kind in ("integer", "decimal"):
        if isinstance(value, bool):
            raise ValueError("Boolean is not numeric")
        n = Decimal(str(value))
        if not n.is_finite():
            raise ValueError("Non-finite numeric value")
        if kind == "decimal":
            return n
        if n != n.to_integral_value():
            raise ValueError("Non-integral integer")
        return int(n)
    raise ValueError(f"Unsupported type: {kind}")


def evaluate(expr, row):
    if not isinstance(expr, dict):
        return expr
    if "column" in expr:
        return row[expr["column"]]
    op = expr["op"]
    args = [evaluate(a, row) for a in expr["args"]]
    if op == "and":
        return False if False in args else (None if None in args else True)
    if op == "or":
        return True if True in args else (None if None in args else False)
    if op == "not":
        return None if args[0] is None else not args[0]
    if op == "is_null":
        return args[0] is None
    if op == "is_not_null":
        return args[0] is not None
    if op in ("in", "not_in"):
        value, options = args
        result = None if value is None else (True if value in [x for x in options if x is not None] else (None if None in options else False))
        return (None if result is None else not result) if op == "not_in" else result
    if any(a is None for a in args):
        return None
    if op in ("like", "contains", "starts_with", "ends_with", "length"):
        if not all(isinstance(a, str) for a in args):
            raise TypeError("Text operations require strings")
    if op == "like":
        pattern = []
        escaped = False
        for char in args[1]:
            if escaped:
                pattern.append(re.escape(char)); escaped = False
            elif char == "\\":
                escaped = True
            else:
                pattern.append(".*" if char == "%" else "." if char == "_" else re.escape(char))
        if escaped:
            raise ValueError("Trailing LIKE escape")
        return re.fullmatch("".join(pattern), args[0], re.DOTALL) is not None
    operations = {
        "eq": lambda a, b: a == b, "ne": lambda a, b: a != b,
        "lt": lambda a, b: a < b, "le": lambda a, b: a <= b,
        "gt": lambda a, b: a > b, "ge": lambda a, b: a >= b,
        "between": lambda a, b, c: b <= a <= c,
        "not_between": lambda a, b, c: not b <= a <= c,
        "contains": lambda a, b: b in a,
        "starts_with": lambda a, b: a.startswith(b),
        "ends_with": lambda a, b: a.endswith(b),
        "length": len, "add": lambda a, b: a+b,
        "subtract": lambda a, b: a-b, "multiply": lambda a, b: a*b,
        "divide": lambda a, b: a/b,
    }
    return operations[op](*args)


def matches(expr, row):
    return evaluate(expr, row) is True


def rows(table):
    table = Path(table)
    schema = json.loads((table / "schema.json").read_text(encoding="utf-8"))
    columns = schema["columns"]
    paths = sorted(table.glob("*.csv"))
    if not paths:
        raise ValueError("No CSV files")
    options = schema["csv"]
    for path in paths:
        with path.open(encoding=options["encoding"], newline="") as stream:
            iterator = csv.reader(stream, delimiter=options["delimiter"],
                                  quotechar=options["quotechar"], strict=True)
            if next(iterator, None) != [c["name"] for c in columns]:
                raise ValueError(f"Header mismatch: {path}")
            for number, values in enumerate(iterator, 2):
                if len(values) != len(columns):
                    raise ValueError(f"Width mismatch: {path}:record {number}")
                result = {}
                for c, text in zip(columns, values):
                    value = None if text == options["null_token"] else text
                    if value is None and not c["nullable"]:
                        raise ValueError(f"Null {c['name']} at {path}:record {number}")
                    try:
                        result[c["name"]] = convert(value, c["type"])
                    except (ValueError, TypeError, ArithmeticError) as error:
                        raise ValueError(f"Invalid {c['name']} at {path}:record {number}: {error}") from error
                yield result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("table", type=Path)
    p.add_argument("--expression", type=Path)
    a = p.parse_args()
    expression = json.loads(a.expression.read_text()) if a.expression else None
    total = sum(1 for row in rows(a.table) if expression is None or matches(expression, row))
    print(json.dumps({"count": total}))


if __name__ == "__main__":
    main()
