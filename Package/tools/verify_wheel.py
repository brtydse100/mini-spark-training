"""Build a wheel and verify it without using the editable source install."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    checks = ROOT / ".wheel-check"
    checks.mkdir(exist_ok=True)
    environment = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
        environment.pop(name, None)

    def run(arguments, cwd):
        subprocess.run([str(a) for a in arguments], cwd=cwd, env=environment, check=True)

    with tempfile.TemporaryDirectory(prefix="verify-", dir=checks) as directory:
        temporary = Path(directory).resolve()
        if not temporary.is_relative_to(checks.resolve()):
            raise RuntimeError("Verification directory is outside its designated root")
        built = temporary / "wheels"
        run([sys.executable, "-m", "build", "--wheel", "--outdir", built, ROOT], temporary)
        wheels = list(built.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("Expected exactly one newly built wheel")
        distribution = ROOT / "dist" / wheels[0].name
        distribution.parent.mkdir(exist_ok=True)
        shutil.copy2(wheels[0], distribution)

        installed = temporary / "environment"
        venv.EnvBuilder(with_pip=True).create(installed)
        python = installed / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run([python, "-m", "pip", "install", distribution, "pytest>=8"], temporary)
        # -I ignores PYTHONPATH and removes the current/script directory from
        # import search. Explicit pytest config avoids pythonpath=src in the
        # source project's pyproject.toml during installed-package checks.
        provenance = temporary / "provenance.json"
        check_import = (
            "import json,pathlib,sys,workframe; "
            "p=pathlib.Path(workframe.__file__).resolve(); "
            "assert p.is_relative_to(pathlib.Path(sys.prefix).resolve()),p; "
            "pathlib.Path(sys.argv[1]).write_text(json.dumps({'module':str(p),'prefix':sys.prefix}))"
        )
        run([python, "-I", "-c", check_import, provenance], temporary)
        config = temporary / "pytest.ini"
        config.write_text("[pytest]\n", encoding="utf-8")
        run([python, "-I", "-m", "pytest", "-c", config,
             "--import-mode=importlib", ROOT / "tests", "-q"], temporary)
        run([python, "-I", ROOT / "tools/smoke.py"], temporary)
        if os.name == "nt":
            run([python, "-I", "-m", "workframe.launcher", "--report",
                 ROOT / "reports/wheel-runtime.json", ROOT / "examples/local_driver.py"], temporary)
        report = {
            "status": "success",
            "wheel": str(distribution),
            "installed_import": json.loads(provenance.read_text()),
            "public_tests": "passed",
            "smoke": "passed",
            "resource_launcher": "passed" if os.name == "nt" else "not_available",
        }
        destination = ROOT / "reports/wheel-check.json"
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wheel verified: {distribution}")
        print(f"Report: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
