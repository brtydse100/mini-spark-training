import importlib.util
from pathlib import Path
from openpyxl import load_workbook


def test_generated_table_equivalence(tmp_path):
    spec = importlib.util.spec_from_file_location("generator", (Path(__file__).resolve().parents[2] / "Exercise") / "tools/make_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.generate(tmp_path, rows=37, parts=4, seed=7, skew=True)
    def read(paths):
        result = []
        for p in paths:
            wb = load_workbook(p, read_only=True)
            try:
                result.extend(list(wb["data"].values)[1:])
            finally:
                wb.close()
        return result
    one = read([tmp_path / "single/part-001.xlsx"])
    many = read(sorted((tmp_path / "multiple").glob("*.xlsx")))
    assert one == many
    assert len(one) == 37
    assert (tmp_path / "multiple/schema.json").exists()


def test_oracle_handles_trailing_blank_cells(tmp_path):
    import importlib.util
    from instructor.reference import rows
    spec = importlib.util.spec_from_file_location("generator2", (Path(__file__).resolve().parents[2] / "Exercise") / "tools/make_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.generate(tmp_path, rows=37)
    assert len(list(rows(tmp_path / "single"))) == 37
    assert len(list(rows(tmp_path / "multiple"))) == 37
