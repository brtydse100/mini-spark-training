# Part 1.5 - Understand Workframe

**When:** after the stage-one application review, before stage two. Allow half to one working day within the first review day. Continue without AI; documentation and debuggers are allowed.

**Goal:** explain how the package runs your code, using a diagram grounded in the source you actually use.

## 1. Follow one real task

Open the Workframe source in the [repository](https://github.com/brtydse100/mini-spark-training/tree/main/Package) and identify the version installed in your environment. Use a simple task from your stage-one application.

Follow its journey: starting executors, submitting the task file and input, crossing a process boundary, executing run(data), returning a result, and collecting that result in the driver. Also follow what happens when the task raises an exception and when the application shuts down.

## 2. Create workframe-internals.drawio

Create an editable draw.io diagram of **the package itself**. Your stage-one architecture.drawio describes your application; this is a different diagram.

Include:

- Relevant modules/functions, with actual names from the code.
- Driver and executor process boundaries, queues, message direction, and JSON conversion.
- Task identity and state: where pending/completed work and input/results are held.
- Loading your Python task file, calling run(data), and collecting success/error results.
- Process startup and shutdown.
- Built-in timing/resource observation and shared resource enforcement; explain their different roles.

Group supporting helpers rather than drawing every function. Label anything you have not verified as an assumption.

## 3. Walk through it with your mentor

Bring the editable file, package version/source location, and your example task/run command. Open the code locations behind the arrows and trace a success, a task error, and shutdown. Explain which responsibilities belong to Workframe and which belong to your application.

**Ready for stage two:** the diagram matches the package behavior and you can explain the execution flow from code. Keep it current as your understanding and implementation evolve.

If you feel stuck or encounter a problem with the exercise, ask your mentor for help.
