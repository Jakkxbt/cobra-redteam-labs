# Lab 09 — Blind SQL Injection

**Impact:** Full database extraction / password theft &nbsp;·&nbsp; **Difficulty:** ⭐⭐⭐⭐
&nbsp;·&nbsp; **Tier:** Harder — you get the *what*, not the *how*.

## What it is

**Blind SQL injection** is a type of SQL injection where the application doesn't return
any actual data from the database — just a yes/no or true/false response. This makes
exploitation harder because you can't see the results directly, but you can still extract
information by asking many yes/no questions.

This lab has a simple endpoint: `GET /check?user=<username>` that returns ONLY "exists" or "does
not exist". No errors, no row data, just a boolean. But the vulnerable implementation builds the
SQL query by **string concatenation**, which means you can inject SQL into the username parameter
to change what the query actually does.

The **safe version** uses a parameterised query, which completely prevents SQL injection.

## Run it

```bash
python3 lab.py            # vulnerable, http://127.0.0.1:18210/
python3 lab.py --safe     # the fixed version
```

Check if users exist:
```bash
curl "http://127.0.0.1:18210/check?user=alice"
# -> exists

curl "http://127.0.0.1:18210/check?user=eve"
# -> does not exist
```

## Your mission

Extract the admin's password from the database. You only get a boolean response —
"exists" or "does not exist" — so you'll need to craft SQL injection payloads that turn this
into a question you can ask repeatedly to extract one character at a time.

When you recover the full password, you're done. The password is the flag.

## Hints — the vuln, and where to point your thinking

This is the harder tier: no step-by-step, and no solution published in this repo. Work it out
— the hints tell you the bug and where to look.

1. **Understand the query structure.** The vulnerable code builds a query like:
   `SELECT 1 FROM users WHERE name='<username>'`
   What happens if the username contains single quotes? Can you make the query always true?

2. **The SUBSTRING trick.** You can't return the password directly, but you can test if the password
   **starts with** a specific character. SQL has a `SUBSTR()` function that extracts part of a
   string. If you can make the boolean result depend on whether a specific character is at a
   specific position, you can test each character one by one.

3. **Boolean logic.** SQL injection lets you use AND/OR in queries. Think about how you can
   make the entire query return true only when a condition is met, even though the application
   only cares whether *any* row exists.

4. **Character set.** What characters might be in the password? Start with letters (a-z, A-Z),
   then numbers (0-9), then special characters (_ - { } etc.). Test systematically.

## The fix (`--safe`)

The safe server closes the vulnerability completely: run `python3 lab.py --safe --port 18294`,
then replay any extraction payload against `:18294` — it will always return "does not exist". It:

- **Uses parameterised queries** — the username is passed as a parameter, not concatenated
- **Prevents injection entirely** — there's no way to change the query structure

## Going deeper

- **Error-based vs blind:** Error-based SQLi reveals database errors that leak information
  (table names, column names, etc.). Blind SQLi is stealthier but slower — you only get
  yes/no responses.
- **Time-based blind:** Some applications use timing to leak information (e.g., sleep when a
  condition is true). This lab is boolean-based, not time-based.
- **Automated blind SQLi:** Tools like `sqlmap --dump --batch --dbs` can automate the
  character-by-character extraction process.
- **Defenses:** Parameterised queries (prepared statements), input validation, allowlisting
  usernames, and using ORM frameworks that handle SQL safely.
