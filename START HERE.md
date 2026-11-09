# Mini Spark Exercise

There are two folders:

1. **Package** is the material trainees work on. It contains the generic Python library, setup/build scripts, examples, initial assignment, and local Excel data. It deliberately does not implement their query engine.
2. **Instructor Guide** is for you. It explains the purpose, setup, stages, solution approaches, planted bugs, review criteria, and reference tools. Do not give this folder to trainees.

Start with [the instructor index](Instructor%20Guide/00%20-%20START%20HERE.md), then [setup](Instructor%20Guide/02%20-%20Setup.md).

Actual library code is in **Package/src/workframe**. Trainees write their application in **Package/trainee**. The empty driver is intentional: it is their assignment.

The library has approximately 1,200 source lines across 14 modules. Everything executes locally on Windows. CPU/memory enforcement and the timer are provided. The code contains deliberate faults; a normal example working does not mean the library handles advanced cases correctly.
