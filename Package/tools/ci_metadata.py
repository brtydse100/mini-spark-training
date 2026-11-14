"""Describe a build and assign an isolated development version on pull requests."""
import json
import os
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def metadata(project, environment):
    source = project.read_text(encoding="utf-8")
    config = tomllib.loads(source)["project"]
    version = config["version"]
    name = config["name"]
    event = environment.get("GITHUB_EVENT_NAME", "local")
    if event == "pull_request":
        run = environment.get("GITHUB_RUN_NUMBER", "")
        if not run.isdecimal() or int(run) < 1:
            raise ValueError("Pull request builds need a positive GITHUB_RUN_NUMBER")
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
            raise ValueError("Pull request versioning expects a release version X.Y.Z")
        version = f"{version}.dev{run}"
        updated, count = re.subn(r'(?m)^version = "[^"\n]+"$', f'version = "{version}"', source)
        if count != 1:
            raise ValueError("Expected one static project version")
        project.write_text(updated, encoding="utf-8")
    return {"name": name, "version": version, "event": event,
            "commit": environment.get("GITHUB_SHA", "local"),
            "run_number": environment.get("GITHUB_RUN_NUMBER", "local")}


def main():
    value = metadata(ROOT / "pyproject.toml", os.environ)
    path = ROOT / "reports/build-metadata.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            for name in ("name", "version"):
                stream.write(f"{name}={value[name]}\n")
    print(json.dumps(value))


if __name__ == "__main__":
    main()
