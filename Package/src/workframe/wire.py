"""JSON transport contracts. No table-specific conversion belongs here."""
import json
from .errors import ProtocolError


def encode(value, max_bytes=None):
    result = json.dumps(value, ensure_ascii=False, allow_nan=False)
    if max_bytes is not None and len(result.encode("utf-8")) > max_bytes:
        raise ProtocolError("Encoded message exceeds configured byte limit")
    return result


def _invalid_constant(value):
    raise ProtocolError(f"Non-finite JSON constant: {value}")


def decode(value, max_bytes=None):
    if not isinstance(value, str):
        raise ProtocolError("Transport expects a JSON string")
    if max_bytes is not None and len(value.encode("utf-8")) > max_bytes:
        raise ProtocolError("Received message exceeds configured byte limit")
    return json.loads(value, parse_constant=_invalid_constant)


def _object(value):
    if not isinstance(value, dict):
        raise ProtocolError("Message must be a JSON object")
    return value


def _identity(value):
    if not isinstance(value, str) or not value:
        raise ProtocolError("Task identity must be nonempty text")


def validate_task(value):
    _object(value)
    _identity(value.get("task_id"))
    if not isinstance(value.get("script"), str) or not value["script"]:
        raise ProtocolError("Task requires a script path")
    if "data" not in value:
        raise ProtocolError("Task requires data, which may be null")
    entrypoint = value.get("entrypoint", "run")
    if not isinstance(entrypoint, str) or not entrypoint.isidentifier():
        raise ProtocolError("Invalid task entry point")
    return value


def validate_result(value):
    _object(value)
    _identity(value.get("task_id"))
    if type(value.get("executor")) is not int or value["executor"] < 0:
        raise ProtocolError("Completion requires an executor index")
    if value.get("status") == "ok":
        if "result" not in value:
            raise ProtocolError("Successful completion requires a result")
    elif value.get("status") == "error":
        detail = _object(value.get("error"))
        if not isinstance(detail.get("type"), str) or not isinstance(detail.get("message"), str):
            raise ProtocolError("Failure requires error type and message")
    else:
        raise ProtocolError("Unknown completion status")
    return value


def success(task_id, executor, result, metrics=None):
    message = {
        "task_id": task_id,
        "executor": executor,
        "status": "ok",
        "result": result,
    }
    if metrics is not None:
        message["metrics"] = metrics
    return validate_result(message)


def failure(task_id, executor, error, traceback_text, metrics=None):
    message = {
        "task_id": task_id,
        "executor": executor,
        "status": "error",
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback_text,
        },
    }
    if metrics is not None:
        message["metrics"] = metrics
    return validate_result(message)


def encoded_size(value):
    return len(encode(value).encode("utf-8"))
