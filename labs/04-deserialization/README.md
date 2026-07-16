# Lab 04 — Insecure Deserialization

**Impact:** Remote code execution &nbsp;·&nbsp; **Difficulty:** ⭐⭐⭐

## What it is

"Deserialization" is turning stored bytes back into a live object. In some languages (Python
`pickle`, Java, PHP, Ruby) the *act of loading* attacker-controlled bytes can be made to run code.
If an app deserializes anything you send it, that's often instant code execution.

## Run it

```bash
python3 vulnerable.py     # http://127.0.0.1:18865/load?data=<base64 pickle>
python3 safe.py           # the fixed version
```

Watch the terminal you started `vulnerable.py` in — that's where server-side output shows up.

## Your mission

Get the server to run a command (`id`) when it deserializes your data.

## Hints — try these before you peek

1. The `data` parameter is base64 that the server **unpickles**. Pickle isn't just data — loading it
   can *call things*.
2. A Python object can define `__reduce__`, which pickle honours on load. What if `__reduce__`
   returned `os.system` and a command?
3. `os.system("id")` prints to the server's own console — so watch the *server* terminal, not the
   HTTP response.

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix (see `safe.py`)

Never unpickle untrusted input. The safe version uses a data-only format (e.g. JSON) or signs/limits
what it will load, so a crafted object can't execute anything.

## Going deeper

- The same idea applies to Java (`ysoserial` gadget chains), PHP (`O:` objects), Ruby (`Marshal`).
- Read why "just deserialize the user's session cookie" is such a common real-world RCE.
