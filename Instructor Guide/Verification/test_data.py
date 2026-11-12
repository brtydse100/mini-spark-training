import csv
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]


def generator():
    spec = importlib.util.spec_from_file_location("generator", ROOT / "Exercise/tools/make_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_table_equivalence(tmp_path):
    generator().generate(tmp_path, rows=37, parts=4, seed=7, skew=True)
    def read(paths):
        result = []
        for path in paths:
            with path.open(encoding="utf-8", newline="") as stream:
                result.extend(list(csv.reader(stream))[1:])
        return result
    one = read([tmp_path / "single/part-001.csv"])
    many = read(sorted((tmp_path / "multiple").glob("*.csv")))
    assert one == many
    assert len(one) == 37
    assert (tmp_path / "multiple/schema.json").exists()
    assert not list(tmp_path.rglob("*.xlsx"))


def test_oracle_converts_text_and_preserves_multiline_records(tmp_path):
    from instructor.reference import rows
    generator().generate(tmp_path, rows=37)
    one = list(rows(tmp_path / "single"))
    assert one == list(rows(tmp_path / "multiple"))
    assert len(one) == 37
    assert one[0]["age"] is None
    assert type(one[0]["id"]) is int
    assert type(one[0]["active"]) is bool
    assert "\n" in one[1]["note"] and '"quoted"' in one[1]["note"]
    assert any(ord(c) > 127 for c in one[1]["note"])


def test_header_only_table_and_no_overwrite(tmp_path):
    from instructor.reference import rows
    generator().generate(tmp_path, rows=0, parts=3)
    assert list(rows(tmp_path / "single")) == []
    assert list(rows(tmp_path / "multiple")) == []
    with pytest.raises(FileExistsError):
        generator().generate(tmp_path, rows=1)


def test_null_token_distinguishes_empty_text_and_rejects_bad_width(tmp_path):
    from instructor.reference import rows
    generator().generate(tmp_path, rows=2)
    path = tmp_path / "single/part-001.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        records = list(csv.reader(stream))
    records[1][-1] = ""
    with path.open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream).writerows(records)
    assert list(rows(tmp_path / "single"))[0]["note"] == ""
    records[1].pop()
    with path.open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream).writerows(records)
    with pytest.raises(ValueError, match="Width mismatch"):
        list(rows(tmp_path / "single"))


def test_default_checkpoint_in_both_layouts(tmp_path):
    from instructor.reference import rows, matches
    generator().generate(tmp_path, rows=1200)
    expression = json.loads((ROOT / "Instructor Guide/Reference/instructor/checkpoint.json").read_text())
    assert sum(matches(expression, row) for row in rows(tmp_path / "single")) == 200
    assert sum(matches(expression, row) for row in rows(tmp_path / "multiple")) == 200
