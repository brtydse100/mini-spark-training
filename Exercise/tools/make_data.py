"""Generate local UTF-8 CSV tables without building a query engine."""
import argparse
import csv
import json
from pathlib import Path
import random

SCHEMA = {"table": "people", "csv": {"encoding": "utf-8", "delimiter": ",", "quotechar": '"', "null_token": "\\N"}, "version": 1, "columns": [
    {"name": "id", "type": "integer", "nullable": False},
    {"name": "name", "type": "string", "nullable": False},
    {"name": "age", "type": "integer", "nullable": True},
    {"name": "salary", "type": "decimal", "nullable": False},
    {"name": "country", "type": "string", "nullable": False},
    {"name": "active", "type": "boolean", "nullable": False},
    {"name": "note", "type": "string", "nullable": True}]}


def records(count, seed):
    rng = random.Random(seed)
    for i in range(count):
        yield (i + 1, ("Alice", "Bob", "Chloe", "David")[i % 4],
               None if i % 17 == 0 else rng.randrange(10, 81),
               f"{rng.randrange(2000, 15000)}.{i % 100:02}",
               ("IL", "US", "GB", "DE")[i % 4], i % 3 != 0,
               None if i % 11 == 0 else ('Line one, "quoted"\n\u05e9\u05d5\u05e8\u05d4 \u05e9\u05e0\u05d9\u05d9\u05d4 ' + "x" * (i % 40)))


def generate(output, rows=1200, parts=4, seed=42, skew=False):
    if type(rows) is not int or rows < 0 or type(parts) is not int or not 1 <= parts <= 100:
        raise ValueError("rows must be a nonnegative integer; parts must be 1..100")
    output = Path(output)
    # Never silently mix new files with an old generated table.
    if any((output / variant).exists() for variant in ("single", "multiple")):
        raise FileExistsError("Choose a fresh output directory")
    for variant in ("single", "multiple"):
        directory = output / variant
        directory.mkdir(parents=True)
        (directory / "schema.json").write_text(json.dumps(SCHEMA, indent=2), encoding="utf-8")
        n = 1 if variant == "single" else parts
        sizes = [rows // n + (i < rows % n) for i in range(n)]
        if skew and n > 1:
            remaining = rows - rows * 8 // 10
            sizes = [rows * 8 // 10] + [remaining // (n-1) + (i < remaining % (n-1)) for i in range(n-1)]
        source = iter(records(rows, seed))
        for index, size in enumerate(sizes, 1):
            path = directory / f"part-{index:03}.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow([c["name"] for c in SCHEMA["columns"]])
                for _ in range(size):
                    row = next(source)
                    writer.writerow([
                        SCHEMA["csv"]["null_token"] if v is None
                        else str(v).lower() if isinstance(v, bool)
                        else v for v in row
                    ])
    (output / "manifest.json").write_text(json.dumps({"format": "csv", "rows_per_table": rows, "parts": parts, "seed": seed, "skew": skew}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    p.add_argument("--rows", type=int, default=1200)
    p.add_argument("--parts", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--skew", action="store_true")
    a = p.parse_args()
    generate(a.output, a.rows, a.parts, a.seed, a.skew)
    print(f"Created equivalent tables at {a.output}")


if __name__ == "__main__":
    main()
