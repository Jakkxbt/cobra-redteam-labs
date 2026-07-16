# Lab 06 — Malicious File Upload

**Impact:** Web shell / code execution &nbsp;·&nbsp; **Difficulty:** ⭐⭐

## What it is

Upload forms that check a file the wrong way (trusting the extension, or the `Content-Type` the
browser claims) can be tricked into storing a script where the server will later run or serve it. Get
an executable file past the filter and reach it back, and you've got a foothold.

## Run it

```bash
python3 vulnerable.py     # http://127.0.0.1:18965/upload  (POST field "file"); served at /uploads/<name>
python3 safe.py           # the fixed version
```

## Your mission

Get a `.php` file past the upload filter and retrieve it from the server.

## Hints — try these before you peek

1. Try uploading a plain `.php` first — see how the filter reacts. Then ask: *what* is the filter
   actually checking?
2. The browser tells the server a `Content-Type` for each upload — and the server might trust it. Can
   a script file *claim* to be an image?
3. After a successful upload the response tells you the path under `/uploads/`. Fetch it back.

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix (see `safe.py`)

Don't trust the extension or the claimed type. The safe version allow-lists real file types, checks
the actual content (magic bytes), renames on store, and serves uploads from a directory that can't
execute anything. Your bypass gets rejected.

## Going deeper

- Try double extensions (`shell.php.jpg`), alternate PHP extensions (`.phtml`, `.php7`), and null-byte
  tricks — why each one works or doesn't.
- Real defence is layered: validation **and** an execute-nothing upload directory.
