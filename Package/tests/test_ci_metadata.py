import importlib.util
from pathlib import Path
import tomllib
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/ci_metadata.py"


def module():
    spec = importlib.util.spec_from_file_location("ci_metadata", SCRIPT)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def project(tmp_path):
    p = tmp_path / "pyproject.toml"
    p.write_text('[project]\nname = "workframe"\nversion = "0.3.0"\n')
    return p


def test_pull_request_build_gets_development_version(tmp_path):
    path = project(tmp_path)
    value = module().metadata(path, {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_RUN_NUMBER": "42"})
    assert value["name"] == "workframe"
    assert value["version"] == "0.3.0.dev42"
    assert tomllib.loads(path.read_text())["project"]["version"] == value["version"]


def test_main_build_keeps_release_version(tmp_path):
    path = project(tmp_path)
    before = path.read_bytes()
    assert module().metadata(path, {"GITHUB_EVENT_NAME": "push"})["version"] == "0.3.0"
    assert path.read_bytes() == before


def test_invalid_build_identity_does_not_change_project(tmp_path):
    path = project(tmp_path)
    before = path.read_bytes()
    with pytest.raises(ValueError):
        module().metadata(path, {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_RUN_NUMBER": "oops"})
    assert path.read_bytes() == before
