# Lab 11 — Race Condition (One-Time Voucher)

**Impact:** Business-logic abuse / credit inflation &nbsp;·&nbsp; **Difficulty:** ⭐⭐⭐
&nbsp;·&nbsp; **Tier:** Harder — you get the *what*, not the *how*.

## What it is

A **race condition** is what happens when two things that should not both "win" run at the
same time and the program does not make them take turns. In web apps the classic shape is a
**check-then-act** sequence that is not atomic: the server looks at state ("is this voucher
still free?"), does some work, then updates state ("mark it used, grant credit"). If two
requests both pass the check before either update lands, both get treated as the first.

This lab is a **one-time voucher** worth a fixed amount of store credit. Redeem it once and
you should be done. If you can make the server honour it **more than once**, the balance will
exceed a single redemption — and that is your flag.

## Run it

```bash
python3 lab.py            # vulnerable, http://127.0.0.1:18212/
python3 lab.py --safe     # the fixed version
```

The voucher code and the credit value are advertised on `GET /`. Redemption is `POST /redeem`.
Your running total is `GET /balance`.

## Your mission

Cash the same voucher enough times that the balance is **higher than one legitimate
redemption**, and read the `FLAG{...}` the server returns when that happens. A single polite
request will not get you there — think about **timing**, not about forging a second code.

## Hints — the vuln, and where to point your thinking

This is the harder tier: no step-by-step, and no solution published in this repo. Work it out —
the hints tell you the bug and where to look.

1. **Name the two steps.** For a one-time code the server must (a) decide the code is still
   unused, and (b) mark it used and grant credit. If those are separate moments in time, what
   can slip between them?
2. **One client, many requests.** You do not need two accounts. What happens if the *same*
   redemption is in flight many times at once against a multi-threaded server?
3. **Widen the window, then measure.** Slow responses are often a gift: they make interleaving
   easier. After a burst, look at **balance** and **how many successes** you got — not just the
   HTTP status of a single call.
4. **The prize condition is business logic.** The flag is not a hidden path; it is the server
   admitting the voucher was honoured past the one-shot rule.

When you land it, a successful over-redemption response (or the balance view after one) carries
a `FLAG{...}`.

## The fix (`--safe`)

The safe server closes the race, and you can see it for yourself: run `python3 lab.py --safe
--port 18213`, then fire the **same concurrent burst** that worked on the vulnerable port —
you should see **exactly one** successful redemption; the rest come back as already used, and
the balance equals one credit grant with **no flag**.

It:

- **Wraps check-and-set in one critical section** (a lock) so only one request can pass the
  "unused" test and perform the update.
- Keeps the same external API — the bug was concurrency control, not a missing password.

## Going deeper

- **TOCTOU** (time-of-check / time-of-use) is the same idea outside HTTP: file permissions,
  coupon systems, seat booking, stock counters, double-spend patterns.
- **Real fixes** at scale: database transactions with row locks, `UPDATE … WHERE used = false`
  that returns `rowcount == 1`, atomic Redis `SETNX`, idempotency keys.
- **The rule:** if two outcomes are mutually exclusive, the decision and the write must be
  one atomic unit — never "read, think, write" on shared state without synchronisation.
