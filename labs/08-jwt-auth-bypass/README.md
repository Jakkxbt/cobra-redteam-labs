# Lab 08 — JWT Authentication Bypass

**Impact:** Full account takeover / privilege escalation &nbsp;·&nbsp; **Difficulty:** ⭐⭐⭐
&nbsp;·&nbsp; **Tier:** Harder — you get the *what*, not the *how*.

## What it is

A **JWT** (JSON Web Token) is the little `xxxxx.yyyyy.zzzzz` string an app gives you after login. Three
base64url parts: a **header** (which says how the token is signed), a **payload** (which says *who you
are* — including your role), and a **signature** that's supposed to make the first two tamper-proof.

The whole security model rests on one thing: the server refusing to believe a token whose signature it
can't verify. When the server is careless about *how* it verifies, an attacker can rewrite the payload —
say, promote themselves to admin — and get the server to accept it. This lab has a careless server.

## Run it

```bash
python3 lab.py            # vulnerable, http://127.0.0.1:18208/
python3 lab.py --safe     # the fixed version
```

You log in as **alice**, role **user**. The prize is `GET /admin`, which demands role **admin**.

## Your mission

Reach `/admin` and read the flag. You are only ever issued a *user* token — so you'll have to produce
an *admin* token the server will trust, without knowing any legitimate admin's credentials.

## Hints — the vuln, and where to point your thinking

This is the harder tier: no step-by-step, and no solution published in this repo. Work it out — the
hints tell you the bug and where to look.

1. **Decode your own token first.** The header and payload are just base64url — read them. What field in
   the payload is the server making its access decision on?
2. **The header is attacker-controlled too.** *You* send the whole token, header included. The header
   names the algorithm the server should use to check the signature. What would happen if you *told* the
   server the token uses an algorithm that requires **no signature at all**?
3. **Or attack the key.** If the signing algorithm is a shared-secret HMAC (HS256), the only thing
   stopping you forging a valid signature is *not knowing the secret*. What if the secret is a word you'd
   find in any wordlist? (`hashcat -m 16500`, `jwt_tool -C -d rockyou.txt`.)

Two different doors into the same room. Either one is a valid solve. When you land it, `/admin` returns
a `FLAG{...}`.

## The fix (`--safe`)

The safe server closes **both** doors, and you can see it for yourself: run `python3 lab.py --safe
--port 18209`, then replay whatever forged token got you in against `:18209` — you'll get `401 invalid
token`. It:

- **Pins the algorithm** — it only accepts `HS256` and rejects anything else, so `none` never gets a
  look-in.
- **Uses a strong, random secret** generated at startup, so there's nothing to crack.

## Going deeper

- **Algorithm confusion (RS256 → HS256):** if a server verifies RS256 tokens but can be tricked into
  treating the token as HS256, an attacker signs a forged token using the server's *public* key as the
  HMAC secret. Same root cause: trusting the header's `alg`.
- **`kid` injection:** the header's `kid` (key id) sometimes feeds a file path or SQL lookup — path
  traversal or injection to control which key verifies the token.
- **The rule:** the server must decide the algorithm and the key, never the token. Treat every field in a
  token you didn't sign as hostile input.
