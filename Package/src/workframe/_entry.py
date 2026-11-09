"""Execute a driver after the launcher resumes its assigned process."""
import runpy
import sys
from pathlib import Path


def main():
    # Spawned workers must not inherit this package module as their main module.
    script = str(Path(sys.argv[1]).resolve(strict=True))
    sys.argv = sys.argv[1:]
    sys.path.insert(0, str(Path(script).parent))
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
