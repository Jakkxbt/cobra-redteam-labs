# Lab 01 — Server-Side Template Injection (SSTI)

**Impact:** Remote code execution &nbsp;·&nbsp; **Difficulty:** ⭐⭐

## What it is

Web apps use template engines (Jinja2, Twig, Freemarker…) to build pages. When user input is
placed *into the template itself* instead of passed *as data*, you can inject template syntax the
server evaluates — and that usually leads to running commands on the server.

## Run it

```bash
python3 vulnerable.py     # http://127.0.0.1:18765/   (injectable ?name=)
python3 safe.py           # the fixed version, on another port
```

## Your mission

Get the server to evaluate an expression *you* control through the `name` parameter — then push
it as far as running a command on the box.

## Hints — try these before you peek

1. First, just see what the page does with your input: visit `?name=hi`. Now stop feeding it a
   plain word, and start feeding it *template syntax*.
2. Template engines evaluate expressions written inside special brackets. What happens if `name`
   is a little bit of **maths** wrapped in the right brackets? Use an *unusual* sum, so a
   coincidental number on the page can't fool you into a false positive.
3. If your sum came back calculated, the engine is **Jinja2**. From an evaluated Jinja2 expression
   you can reach Python's internals — think about how you'd get from a template expression to the
   `os` module.

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix (see `safe.py`)

Never render user input as template *source*. Pass it as a **variable** into a static template and
keep autoescaping on. `safe.py` does exactly that — fire the same payloads at it and watch them come
back as harmless literal text.

## Going deeper

- Try the idea against other engines (Twig `{{7*7}}`, Freemarker `${7*7}`, ERB `<%= 7*7 %>`).
- Read up on Jinja2 sandbox escapes and why `__globals__` is the usual road from expression to RCE.
