# CobraSEC Red Team Labs

Hands-on labs for learning to **find, prove, and fix** the web vulnerabilities that matter in a real
red-team engagement. Every lab is a **matched pair** — a deliberately vulnerable target and a
fixed/safe version — with a briefing and **clues** that point you at the bug and where to look.

No cloud, no signup. Each lab runs on localhost with nothing but Python.

> **No answer keys here — on purpose.** Every lab gives you the bug class and clues; landing the
> exploit yourself is the point. Compare your result against each lab's `--safe` version to confirm
> you've actually got it and understand the fix.

> ## ⚠️ Localhost only — do NOT deploy these
> These apps are **deliberately vulnerable**. Run them on **your own machine only** (`127.0.0.1`).
> **Never** put them on a public or internet-facing server — you *will* get compromised. They are
> practice targets, not products.

## Why this is different

Most practice apps just hand you something broken. Here, every bug class comes with:

- a **vulnerable** target *and* a **safe** one — so you learn the fix, not just the break,
- **clues in the open** that name the bug and point you where to look — but no walkthrough to copy,
  so you actually solve it,
- and a plain-English explanation of **why** it works and **how** to close it.

Learn the bug, prove it yourself, then learn to kill it.

## The labs

| # | Lab | Bug class | Impact | Difficulty |
|---|-----|-----------|--------|------------|
| 01 | [ssti](labs/01-ssti) | Server-side template injection | Remote code execution | ⭐⭐ |
| 02 | [xxe](labs/02-xxe) | XML external entity | File disclosure / SSRF | ⭐⭐ |
| 03 | [ssrf](labs/03-ssrf) | Server-side request forgery | Internal network access | ⭐⭐ |
| 04 | [deserialization](labs/04-deserialization) | Insecure deserialization | Remote code execution | ⭐⭐⭐ |
| 05 | [idor](labs/05-idor) | Broken access control | Other users' data | ⭐ |
| 06 | [file-upload](labs/06-file-upload) | Malicious upload | Web shell | ⭐⭐ |
| 07 | [command-injection](labs/07-command-injection) | OS command injection | Remote code execution | ⭐⭐ |

### Harder tier — you get the *what*, not the *how*

Same matched-pair format, but the hints only tell you the bug class and where to point your thinking —
no step-by-step. The full worked solution is still there, collapsed, as a safety net when you're stuck.

| # | Lab | Bug class | Impact | Difficulty |
|---|-----|-----------|--------|------------|
| 08 | [jwt-auth-bypass](labs/08-jwt-auth-bypass) | JWT verification flaws | Privilege escalation / ATO | ⭐⭐⭐ |
| 10 | [graphql](labs/10-graphql) | GraphQL introspection + broken resolver auth | Sensitive data exposure | ⭐⭐⭐ |
| 11 | [race](labs/11-race) | Race condition (check-then-act) | Business-logic abuse / credit inflation | ⭐⭐⭐⭐ |

*More labs added over time — check back.*

## How to run any lab

```bash
cd labs/01-ssti
python3 vulnerable.py      # (or lab.py) — the target, attack this
python3 safe.py            # (or lab.py --safe) — the fix, watch your exploit stop working
```

Then open that lab's `README.md` for the mission, hints, and (when you're ready) the solution.

## Who it's for

Beginners learning web security · red teamers sharpening one bug class · CTF players · anyone prepping
for OSCP / PNPT-style exams.

## Authorised use only

These are self-contained localhost labs for your own practice. The techniques apply only to systems
you own or are explicitly authorised to test.

## License

MIT — see [LICENSE](LICENSE).
