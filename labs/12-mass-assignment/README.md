# Lab 12 — Mass Assignment (Privilege Escalation)

**Impact:** Privilege escalation / broken access control &nbsp;·&nbsp; **Difficulty:** ⭐⭐
&nbsp;·&nbsp; **Tier:** Harder — you get the *what*, not the *how*.

## What it is

**Mass assignment** is what happens when a server takes a bag of fields a client sent and
binds *all* of them straight onto an object — without deciding which fields a client is
actually allowed to set. A "update my profile" endpoint is meant to let you change your
name and email. But if it blindly copies **every** key in your JSON onto your user record,
you can also set the keys it never meant to expose — like the one that says whether you're
an admin.

This lab has a normal user and an admin-only secret. Change the fields you're *supposed*
to change and nothing interesting happens. Change a field you were never meant to touch,
and you promote yourself.

## Run it

```bash
python3 lab.py            # vulnerable, http://127.0.0.1:18122/
python3 lab.py --safe     # the fixed version
```

You have one account: **`trainee` / `training`**. Log in at `POST /login`, view yourself at
`GET /profile`, update yourself at `POST /profile/update` (JSON), and the prize lives behind
`GET /admin/flag`.

## Your mission

Log in as the ordinary `trainee`, become an administrator **without any admin credentials**,
and read the `FLAG{...}` that only an admin can see.

## Hints — the vuln, and where to point your thinking

This is the harder tier: no step-by-step, and no solution published in this repo. The hints
tell you the bug and where to look — the moves are yours.

1. **Read yourself first.** `GET /profile` shows every field the server keeps on you. Some of
   those fields decide what you're allowed to do. Which one looks like it controls access?
2. **What does "update" actually accept?** The endpoint is advertised as name/email. But look
   at what comes *back* after an update — does the server only change what it promised, or does
   it echo changes to fields you didn't expect it to let you set?
3. **Send more than it asked for.** If the update handler copies your whole JSON body onto your
   record, then any field you *name* is a field you *set*. Put the access-control field in your
   update body and see what sticks.
4. **Then walk through the front door.** Once your record says you're privileged, the admin-only
   route stops saying no.
5. **Compare with `--safe`.** The fixed version accepts the same request but only honours an
   allow-list of fields. Watch what it silently ignores — that difference *is* the lesson.
