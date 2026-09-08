# agent-gates — guardrails, circuits and skills for an agent fleet

Gates that **refuse in pure code**, the circuits that order them, and the
skills an agent loads to do a job the same way twice.

No model call. No network. A gate is a small script: same input, same
verdict, always. That is the point — a decision that is not speculative
should not be handed to a language model.

## Why this exists

An agent that can act needs somewhere that says no. Not a prompt asking it
to behave — a process that exits non-zero. These gates run as hooks around
an agent's tool calls: before a command, before a file write, before the
agent claims it is finished.

Each gate here was born from a real failure, and the docstring says which
one. A gate with no story behind it is a guess.

## What is in here

| Folder | What it holds |
|---|---|
| `gates/` | the guardrails, one file each, plus what they refuse |
| `tests/` | one test per gate — each proves the gate **refuses** |
| `circuits/` | the ordered trials a piece of work crosses before it ships |
| `skills/` | procedures an agent loads: how to search, how to prove, how to report |

## Install

Requires Python 3.9+ and bash. Nothing else — no dependencies to install.

```bash
git clone https://github.com/fotsopatrick/agent-gates
cd agent-gates
```

## Run the checks

```bash
python3 verifier.py        # audits this repository against its own claims
bash tests/run-all.sh      # runs every gate's test
```

`verifier.py` does not trust this README. It reads the disk and checks nine
things, including: no secret in any file, no absolute path tied to one
machine, no byte-identical duplicate file, every gate has a test, and a
continuous-integration workflow that actually runs this audit on every push.
It exits non-zero when a claim here is not supported by the files.

That last check exists because of a repository of mine that promised an
audit "failing the build" while shipping no build at all. The gate now
refuses that shape.

## Wiring a gate into Claude Code

A gate reads a JSON event on standard input and exits 0 to allow or 2 to
block. In `~/.claude/settings.json`:

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Bash",
  "hooks": [ { "type": "command",
               "command": "python3 /path/to/gates/porte-secrets.py" } ] } ] } }
```

`PreToolUse` means "before the agent runs a tool". `matcher` picks which
tool. Exit code 2 refuses the call and the message goes back to the agent.

## The two rules the gates encode

**Meeting the condition is the only normal way through.** No override, no
human favour, no password. A gate that refuses is doing its job.

**A gate that has never refused anything is a promise, not a guard.** So
every gate ships with a test that makes it say no, and a test that makes it
stay quiet — a guard that fires on everything guards nothing.

## Language

The gate code and its comments are in French, the language they were written
and argued in. The interfaces, this README and the circuits are in English.
Translating the reasoning would flatten it; the docstrings carry the failure
each gate was born from.

## Licence

Apache 2.0. See `LICENSE`.
