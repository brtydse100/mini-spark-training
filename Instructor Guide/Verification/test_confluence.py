from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def test_trainee_pages_are_concise_and_do_not_disclose_dependency_work():
    pages = sorted((ROOT / "Exercise/confluence").glob("*.md"))
    assert len(pages) == 3
    for page in pages:
        text = page.read_text(encoding="utf-8")
        assert len(text.split()) < 550
        assert len(re.findall(r"^## [0-9]+\.", text, re.M)) >= 3
        assert not re.search(r"\b(defect|fault|patch|repair|tweak|spaghetti)\b", text, re.I)
        assert text.rstrip().endswith("If you feel stuck or encounter a problem with the exercise, ask your mentor for help.")
