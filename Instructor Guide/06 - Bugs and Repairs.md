# Planted library problems and answers

Do not share this document with trainees.

## Structural problems

Runtime._do mixes submission, result tracking, pseudo-caching, batch iteration, and reporting. Names such as _x, a, b, and v hide meaning. Some functions return unrelated types. Internal contracts are weakly documented. The educational repair is to identify responsibilities and introduce useful boundaries while preserving behavior, not to add classes indiscriminately.

## 1. Pending work keyed by executor

Source: Package/src/workframe/runtime.py. _x[executor] holds only one task ID. Submit two tasks to one executor before receiving, and the second overwrites the first. The first completion raises Task/result identity mismatch.

Repair: track active tasks by task ID with the owning executor as data. Validate the returning task ID/owner and remove that exact entry. Reject duplicate active identities or define a clear alternative contract.

## 2. Stale completed results

_done stores results under task ID. Reusing an ID with changed input returns a previous result instead of executing the new work. Sum [1], then reuse its completed ID for sum [9]: the starter returns 1 again.

Repair: remove implicit result reuse. A task ID is not a content-aware query cache. Do not let completed IDs silently bypass execution. Repeated-query tests must cover changed input, not just identical work.

## 3. Completed input retained forever

_history holds every serialized submitted payload. Memory grows with total historical work even when only one task is active. Inspect retained payload references during a long sequential run.

Repair: release input ownership after work no longer needs it. Keep diagnostics bounded and metadata-only. Do not require Python immediately to return every freed allocation to the OS as proof; verify that the retaining references are gone.

## 4. Non-uniform type contracts

settings.amount returns strings unchanged, floats unchanged, and integers on other paths. A batch limit may be 4, 4.0, or "4". submit_many(limit="2") fails in a comparison. pending returns a string zero or integer, and submit_many can return a list or integer zero.

Repair: define accepted representations, validate, normalize semantic integer quantities, and use consistent empty returns. Reject non-integral capacities; do not indiscriminately convert legitimate task data. Remember that "0" is truthy while 0 is false.

## Reference repair and checks

Reference/instructor/fixed_runtime.py demonstrates repairs for these four cases. Verification contains passing normal checks and strict expected failures for the starter. After a trainee fixes code, XPASS means the marked defect no longer reproduces; update the instructor check expectation rather than undoing the repair.

The Windows resource manager, timer, bounded event logger, and build/setup scripts do not contain intentional faults. Some modules can be left unchanged. Give focused investigation scenarios if a valid trainee design avoids one faulty execution path.
