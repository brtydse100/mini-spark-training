"""Observe generic execution; no table/query logic is implemented here."""
from pathlib import Path
from workframe import Runtime, ExecutionOptions


def main():
    options = ExecutionOptions(queue_capacity=2, event_capacity=50)
    task = Path(__file__).with_name("operation.py")
    with Runtime(2, options=options) as runtime:
        runtime.submit(0, task, {"values": [1, 2]}, "a")
        runtime.submit(1, task, {"values": [3, 4]}, "b")
        for result in runtime.receive_many(2):
            print(result)
        runtime.export_diagnostics("reports/runtime.json", "reports/events.jsonl")
        print(runtime.inspect()["task_time_window"])


if __name__ == "__main__":
    main()
