from pathlib import Path
from instructor.fixed_runtime import FixedRuntime
from instructor.reference import matches, convert

TASK = (Path(__file__).resolve().parents[2] / "Package") / "examples/operation.py"

def test_fixed_pipeline_reuse_and_release():
    with FixedRuntime(1) as r:
        r.submit_many(0, [{"script": TASK, "data": {"values": [x]}, "task_id": str(x)} for x in (1, 2)], limit="2")
        assert [r.receive(10)["result"], r.receive(10)["result"]] == [1, 2]
        r.submit(0, TASK, {"values": [9]}, "1")
        assert r.receive(10)["result"] == 9
        assert not r._history
        assert r.pending() == 0

def test_predicates_and_types():
    row = {"age": 25, "name": "Alice", "missing": None}
    col = lambda n: {"column": n}
    assert matches({"op": "and", "args": [
        {"op": "between", "args": [col("age"), 18, 30]},
        {"op": "like", "args": [col("name"), "A%"]},
        {"op": "gt", "args": [{"op": "length", "args": [col("name")]}, 3]}]}, row)
    assert not matches({"op": "not", "args": [{"op": "eq", "args": [col("missing"), 1]}]}, row)
    assert convert("28", "integer") == 28
