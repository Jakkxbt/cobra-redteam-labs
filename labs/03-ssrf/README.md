# Lab 03 — Server-Side Request Forgery (SSRF)

**Impact:** Reach internal-only services / cloud metadata &nbsp;·&nbsp; **Difficulty:** ⭐⭐

## What it is

Some apps fetch a URL *you* supply (previews, webhooks, "import from URL"). If they don't restrict
where they'll go, you can make the **server** request things *you* can't reach directly — internal
admin panels, databases, or a cloud provider's metadata service.

## Run it

```bash
python3 server.py     # app on http://127.0.0.1:18080  + an internal-only service on :18081
```

The `/vulnerable?url=` endpoint fetches whatever URL you give it and returns the body. There's a
service on `127.0.0.1:18081/internal` that is *not* meant to be reachable from outside.

## Your mission

Read the internal-only service through the app.

## Hints — try these before you peek

1. The app fetches a URL *for you* and shows you the result. What can the *server* reach that *you*
   can't?
2. `localhost` / `127.0.0.1` from the server's point of view is the server itself. There's something
   listening internally on port **18081**.
3. Compare the response for a normal external URL vs an internal one.

> **No solution is published here** — that's deliberate. Work it from the hints above and the fixed
> ("safe") version below; proving it yourself is the whole point.

## The fix

The `/safe` endpoint uses an **allow-list** — it only fetches approved hosts and refuses internal
IPs. Try your payload against `/safe?url=...` and watch it get rejected.

## Going deeper

- Read about *blind* SSRF and using an out-of-band listener to confirm it when nothing's reflected.
- Look up the cloud metadata endpoints (AWS/GCP/Azure) that SSRF is famous for reaching.
