"""Load ordinary Python task files without requiring a web service."""
import importlib.util
import inspect
from pathlib import Path
import uuid
from .errors import TaskLoadError


def resolve_script(path):
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file() or source.suffix.lower() != ".py":
        raise TaskLoadError(f"Expected a Python task file: {source}")
    return source


def _module(source):
    name = "workframe_task_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise TaskLoadError(f"Cannot load Python task: {source}")
    module = importlib.util.module_from_spec(spec)
    # Imports and module-level statements execute here, inside the executor.
    spec.loader.exec_module(module)
    return module


def load(path, entrypoint="run"):
    source = resolve_script(path)
    module = _module(source)
    fn = getattr(module, entrypoint, None)
    if not callable(fn):
        raise TaskLoadError(f"{source} must define {entrypoint}(data)")
    if inspect.iscoroutinefunction(fn) or inspect.isgeneratorfunction(fn):
        raise TaskLoadError("Task entry points must return a concrete JSON value")
    try:
        inspect.signature(fn).bind({})
    except (TypeError, ValueError) as error:
        raise TaskLoadError(f"{entrypoint} must accept one positional data argument") from error
    return fn


def inspect_task(path, entrypoint="run"):
    """Inspect syntax without running module-level code in the driver.

    This is a lightweight discovery helper, not a promise that execution will
    succeed. Decorators, imports, and dynamic attributes are resolved at load.
    """
    import ast
    import tokenize
    source = resolve_script(path)
    with tokenize.open(source) as stream:
        tree = ast.parse(stream.read(), filename=str(source))
    definitions = [node for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    selected = next((node for node in definitions if node.name == entrypoint), None)
    if selected is None:
        raise TaskLoadError(f"No top-level {entrypoint} function in {source}")
    return {
        "path": str(source),
        "entrypoint": entrypoint,
        "line": selected.lineno,
        "async": isinstance(selected, ast.AsyncFunctionDef),
        "parameters": [argument.arg for argument in selected.args.args],
        "size_bytes": source.stat().st_size,
    }
