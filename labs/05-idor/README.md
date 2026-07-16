# Lab 05 — IDOR / Broken Access Control

**Impact:** Read (or change) other users' data &nbsp;·&nbsp; **Difficulty:** ⭐

## What it is

IDOR = Insecure Direct Object Reference. An app lets you access a record by its id (`/order/42`)
but forgets to check the record is actually *yours*. Change the id, get someone else's data. It's
one of the most common — and most damaging — web bugs, and it needs no special tricks.

## Run it

```bash
python3 lab.py            # vulnerable, http://127.0.0.1:18190/
python3 lab.py --safe     # the fixed version
```

You're logged in as **alice** (you own orders **1** and **2**). Order **3** belongs to **bob**.

## Your mission

Read bob's order — including his card details — as alice.

## Hints — try these before you peek

1. Look at your own orders first: `GET /api/order/1?user=alice` and `/api/order/2?user=alice`.
2. The record id is right there in the URL, and it's just a number.
3. What happens if you ask for an id that *isn't* one of yours?

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix (`--safe`)

The safe version checks `order.owner == you` and returns **403 Forbidden** for anything that isn't
yours. Try your payload against it:

```bash
python3 lab.py --safe --port 18191
# replay whatever request read another user's order, now against :18191   -> 403 forbidden
```

## Going deeper

- IDOR isn't only reads — the same missing check on an *update* or *delete* lets you change other
  people's data.
- Real apps hide the id (UUIDs, "current user" lookups) — but hiding isn't fixing. The fix is always
  the ownership check.
