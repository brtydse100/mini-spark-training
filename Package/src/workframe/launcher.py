"""Run a local driver under one enforced budget and write a JSON report."""
import argparse
import math
import sys
import time
from pathlib import Path
from .metrics import save_report
from .resources import Job, Budget
from .process import SuspendedProcess


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Expected a finite positive number")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--label", default="development")
    parser.add_argument("--cpu-percent", type=positive)
    parser.add_argument("--memory-mb", type=int)
    parser.add_argument("--timeout", type=positive)
    parser.add_argument("--report", type=Path, default=Path("reports/run.json"))
    parser.add_argument("script", type=Path)
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        budget = Budget.load(args.profile) if args.profile else Budget()
        budget = budget.override(cpu_percent=args.cpu_percent, memory_mb=args.memory_mb,
                                 timeout=args.timeout)
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    args.cpu_percent = budget.cpu_percent
    args.memory_mb = budget.memory_mb
    args.timeout = budget.timeout
    script = args.script.resolve(strict=True)
    report = {"status": "launcher_error", "cpu_percent": args.cpu_percent,
              "memory_limit_bytes": args.memory_mb * 1024 * 1024,
              "timeout_seconds": args.timeout, "script": str(script)}
    import platform
    import os
    report["schema_version"] = 1
    report["label"] = args.label
    report["environment"] = {
        "python": platform.python_version(),
        "executable": sys.executable,
        "system": platform.system(),
        "machine": platform.machine(),
        "logical_processors": os.cpu_count(),
    }
    report["samples"] = 0
    child = None
    job = None
    started = time.perf_counter()
    code = 1
    try:
        job = Job(args.cpu_percent, args.memory_mb)
        child = SuspendedProcess([sys.executable, "-m", "workframe._entry", str(script), *args.args])
        report["enforced_limits"] = job.limits()
        job.assign(child)
        child.resume()
        while True:
            exit_code = child.poll()
            sample = job.sample()
            report["samples"] += 1
            if exit_code is not None and sample["active_processes"] == 0:
                code = 0 if exit_code == 0 else 1
                report["status"] = "success" if code == 0 else "failed"
                report["exit_code"] = exit_code
                break
            if time.perf_counter() - started >= args.timeout:
                report["status"] = "timeout"
                job.terminate()
                child.wait(timeout=10)
                break
            if exit_code is not None and sample["active_processes"]:
                report["status"] = "orphan_processes"
                job.terminate()
                child.wait(timeout=10)
                break
            time.sleep(.01)
        report.update(job.wait_empty())
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        print(report["error"], file=sys.stderr)
    finally:
        if job is not None:
            job.close()
        if child is not None:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=10)
            child.close()
        report["elapsed_seconds"] = time.perf_counter() - started
        save_report(args.report, report)
    print(f"{report['status']}: {report['elapsed_seconds']:.3f}s; report: {args.report}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
