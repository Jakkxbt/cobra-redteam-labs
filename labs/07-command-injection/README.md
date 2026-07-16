# Lab 07 — OS Command Injection

**Impact:** Remote code execution &nbsp;·&nbsp; **Difficulty:** ⭐⭐

## What it is

When an app builds a shell command out of your input (ping this host, convert this file, look up that
domain), the shell treats certain characters as *"and now run this too."* Slip those in and your
commands run on the server alongside the app's.

## Run it

```bash
python3 lab.py            # http://127.0.0.1:18180/vulnerable?input=...  and  /safe?input=...
```

## Your mission

Make the server run your command (`id`) and show you the output.

## Hints — try these before you peek

1. Your `input` gets dropped into a shell command. The shell has special characters that *chain*
   commands.
2. `;` runs a second command. `|` pipes into one. `$( )` and backticks run a command and substitute
   its output.
3. You want the output of *your* command to come back in the response — which separator gives you
   that?

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix (`/safe`)

The safe endpoint never invokes a shell — it passes arguments as a list (no shell parsing), so your
metacharacters are just literal text. Replay the same payload that worked above against
`/safe?input=...` and watch it do nothing.

## Going deeper

- When output isn't reflected ("blind"), prove it with a timing trick: `input=;sleep 5`.
- The universal fix: don't build shell strings from input — use argument lists / safe APIs.
