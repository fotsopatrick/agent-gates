# Circuits — a gate is a trial, not paperwork

A **circuit** is an ordered set of gates a piece of work must cross before it
reaches the outside world. A gate is not a checkbox: it is a condition that
can **refuse**. A gate that has never refused anything is a promise, not a
guard.

Four objects, and nothing more:

| Object | What it is |
|---|---|
| `model` | the template: this kind of work crosses these gates, in this order |
| `step` | one gate: its condition, and what it refuses |
| `instance` | one piece of work currently crossing a model |
| `crossing` | the record: which gate, when, passed or refused, and why |

**The rule that makes it work:** a step is passed only when its condition is
*met*, and meeting the condition is the normal path — no password, no
override, no human favour. The only way past a gate that refuses is to fix
the work.

**The rule that makes it honest:** `crossing` is append-only. A refusal is
never deleted. A circuit whose crossings show zero refusals is either
guarding nothing, or lying.

The three templates in this folder are plain JSON so any runtime can read
them. `sequence` numbers leave gaps (10, 20, 30) so a gate can be inserted
later without renumbering.
