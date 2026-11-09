"""Generate local literal-value XLSX tables without building a query engine."""
import argparse
import json
from pathlib import Path
import random
from openpyxl import Workbook

SCHEMA = {"table": "people", "sheet": "data", "version": 1, "columns": [
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
               None if i % 11 == 0 else ('Line one, "quoted"\n???? ????? ' + "x" * (i % 40)))


def generate(output, rows=1200, parts=4, seed=42, skew=False):
    if not 0 <= rows <= 1_048_575 or not 1 <= parts <= 100:
        raise ValueError("rows must be 0..1048575; parts must be 1..100")
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
            wb = Workbook(write_only=True)
            ws = wb.create_sheet("data")
            ws.append([c["name"] for c in SCHEMA["columns"]])
            for _ in range(size):
                ws.append(next(source))
            wb.save(directory / f"part-{index:03}.xlsx")
            wb.close()
    (output / "manifest.json").write_text(json.dumps({"rows_per_table": rows, "parts": parts, "seed": seed, "skew": skew}, indent=2))


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
