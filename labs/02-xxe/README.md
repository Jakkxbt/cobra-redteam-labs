# Lab 02 — XML External Entity (XXE)

**Impact:** Local file disclosure / SSRF &nbsp;·&nbsp; **Difficulty:** ⭐⭐

## What it is

Old XML parsers will fetch *external entities* — references that point at a file or a URL — and
paste the contents into the document. If an app parses XML you send it with that behaviour left on,
you can make it read local files off the server (or reach internal services).

## Run it

```bash
python3 vulnerable.py     # http://127.0.0.1:8081/xxe   (POST XML here)
python3 safe.py           # the fixed parser, http://127.0.0.1:8082/xxe
```

## Your mission

Make the server read a local file — `/etc/passwd` — and hand you its contents.

## Hints — try these before you peek

1. The endpoint takes **XML** by POST. Normal XML has a `<!DOCTYPE>` — and a DOCTYPE can *define
   entities*.
2. An entity can be `SYSTEM "file:///some/path"`. Define one, then *use* it (`&yourentity;`) inside
   the body so it lands in the output.
3. Look for the file's contents (a line starting `root:`) coming back in the response.

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix (see `safe.py`)

Disable external entities / DTDs in the parser (Python: `defusedxml`). The safe version rejects the
entity and returns an error instead of the file.

## Going deeper

- Try `file:///etc/hostname`. What else is world-readable and interesting?
- Read about *blind* XXE and out-of-band exfiltration for when the content isn't reflected back.
