"""Verify a local Workframe installation using two executor processes."""
from pathlib import Path
from workframe import Runtime


def main():
    task = Path(__file__).resolve().parents[1] / "examples/operation.py"
    with Runtime(2) as r:
        r.submit(0, task, {"values": [1, 2, 3]}, "one")
        r.submit(1, task, {"values": []}, "two")
        actual = sorted(r.receive(15)["result"] for _ in range(2))
        if actual != [0, 6]:
            raise AssertionError(actual)
    print("Workframe installation and local execution checks passed.")


if __name__ == "__main__":
    main()
