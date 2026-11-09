# Purpose of the exercise

Audience: developers who can already code and know OOP and SOLID. The goal is to become confident navigating, explaining, changing, and extending unfamiliar code, and to experience why conventions and clear responsibilities matter.

Trainees build a small Spark-like engine using a generic, imperfect execution skeleton. Their application understands Excel tables and queries. The library understands processes, Python task files, JSON messages, and execution state.

The library already contains tangled functions, poor names and documentation, inconsistent types, and faulty assumptions. Simple initial tasks work. More demanding tasks expose real correctness and memory problems in code trainees already depend on. Other modules work and can be left alone.

Required engine features: filter, count, show; one table in one or multiple .xlsx files; an external schema.json; partitioning; balanced work; and lazy evaluation. A driver creates multiple executors. Executors receive JSON instructions pointing to Python task code and return JSON results.

The exercise takes about ten full-time working days including reviews. It is completed without AI. Documentation, debuggers, profilers, and supplied verification tools are allowed. They must verify behavior, but do not have to write an automated test suite.

Do not reward the number of classes or renamed variables. Reward correct behavior, a clear explanation, targeted improvements, sound responsibility boundaries, and measured performance under a fixed budget.
