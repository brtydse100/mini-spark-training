"""Transport/lifecycle demonstration only; implement your own table driver."""
from pathlib import Path
from workframe import Runtime


def main():
    task = Path(__file__).with_name("operation.py")
    with Runtime(2) as runtime:
        runtime.submit(0, task, {"values": [1, 2, 3]}, "first")
        runtime.submit(1, task, {"values": [4, 5]}, "second")
        for _ in range(2):
            print(runtime.receive())


if __name__ == "__main__":
    main()
