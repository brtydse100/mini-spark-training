# Part 1.5 - Mentor package walkthrough

**Read with:** [part-1.5 brief](../stages/stage-1.5.md). **Time:** half to one day within the first review day, after the application review and before stage two. No AI.

**Successful outcome:** the trainee explains Workframe from the source and traces a real task through an accurate editable workframe-internals.drawio.

## 1. Prepare the walkthrough

Ask for the installed package version, corresponding source, diagram, and a simple stage-one task/run command. Use the actual version: do not assess an installed wheel against unrelated code. This is an understanding checkpoint, not a requirement to redesign the package or predict its defects.

Ask them to run one successful task and one task that raises an exception. Follow the process lifecycle as well as the result. Let them use a debugger or inspect the code when uncertain; distinguish an honest unresolved assumption from an invented explanation.

## 2. Follow the expected flow

For the starter version, an acceptable diagram/code trace includes:

1. Runtime construction/start and ExecutionOptions; spawn creates executor processes and queues.
2. submit or submit_task/TaskSpec passes task identity, script path, and data to Runtime._do; wire helpers serialize JSON before the input queue.
3. worker.work reads the message in the executor; _pack uses loading.load to find the task-file entry point and calls run(data).
4. Success/error messages cross the result queue. Runtime.receive decodes/checks them and returns a result or raises TaskError with remote details.
5. Pending/completed task identity and retained data live in the runtime; the diagram identifies ownership rather than merely drawing arrows.
6. Runtime.close sends sentinels, waits/joins, and terminates remaining processes when needed.
7. ResourceMonitor/process_tree observes resources; launcher/resources.Job enforces/accounts for the aggregate Windows budget. Observation alone does not enforce it.

Group helper modules where appropriate. A task failure normally becomes a transported error; it is not the same as the executor process disappearing.

## 3. Ask questions and inspect the diagram

| Ask | Evidence to look for |
| --- | --- |
| Where does your run(data) execute? | Executor process boundary and actual loading/call site |
| What crosses the boundary? | JSON-compatible data/result and task metadata, rather than a shared live Python object |
| How is a completion associated with its task? | Actual identity/state lookup, not an assumption about completion order |
| What changes when the task raises? | Error packing, transport, receive, and the driver's handling |
| What stops the processes? | Context manager/close path and fallback termination |
| What measures resources, and what limits them? | Clear distinction between sampled monitoring and Job enforcement |

- [ ] The editable file uses relevant actual module/function names.
- [ ] Both process boundaries and message direction are visible.
- [ ] Input/state/result ownership and startup/shutdown are covered.
- [ ] The trainee can open the code behind selected arrows.
- [ ] Application query logic is distinguished from package execution machinery.

Do not give them a reference picture to copy. Stage one's application architecture or a generic Spark diagram does not satisfy this checkpoint.

## 4. Decide

**Ready:** the diagram matches code and the trainee explains success, failure, and shutdown. Minor gaps can be recorded and corrected during the walkthrough. **Needs another review:** missing process boundaries, unexplained task execution/result handling, or confusing measurements with enforcement.

Keep the diagram for stage two and update it as implementation/understanding changes. Package-defect reproductions and repair guidance stay in the [stage-two mentor guide](phase-2.md), where advanced workloads make them relevant.
