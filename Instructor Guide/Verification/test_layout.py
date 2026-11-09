from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[2]


def test_library_has_independent_identity_and_dependencies():
    metadata = tomllib.loads((ROOT / "Package/pyproject.toml").read_text())
    assert metadata["project"]["name"] == "workframe"
    assert "openpyxl" not in str(metadata["project"].get("optional-dependencies", {}))
    assert (ROOT / "Exercise/requirements.txt").exists()


def test_package_contains_no_assignment_or_answer_material():
    package = ROOT / "Package"
    for name in ("trainee", "course", "data", "instructor"):
        assert not (package / name).exists()
    assert not (package / "tools/make_data.py").exists()
    for path in [package / "README.md", package / "CONTRIBUTING.md",
                 package / "pyproject.toml", *(package / "src/workframe").glob("*.py")]:
        assert not re.search(r"\b(trainee|instructor|training|exercise|planted)\b", path.read_text(encoding="utf-8"), re.I), path
    assert (ROOT / "Exercise/data/samples/single/schema.json").exists()
    assert (ROOT / "Exercise/starter/driver.py").exists()
