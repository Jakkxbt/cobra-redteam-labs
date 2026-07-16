# Lab 10 — GraphQL Schema Discovery & Resolver Abuse

**Impact:** Sensitive data exposure / broken access control &nbsp;·&nbsp; **Difficulty:** ⭐⭐⭐
&nbsp;·&nbsp; **Tier:** Harder — you get the *what*, not the *how*.

## What it is

**GraphQL** lets a client ask an API for exactly the fields it needs. Instead of many fixed REST
endpoints, a GraphQL service publishes a schema made of types, fields and arguments, then runs a
resolver for every field in your query.

That flexibility creates two separate security questions. First: can a caller discover fields the
normal interface never shows? Second: does every sensitive resolver independently check whether that
caller is allowed to use it? A hidden button is not an access-control boundary. This lab has a tidy
public interface and a much less tidy schema behind it.

## Run it

```bash
python3 lab.py            # vulnerable, http://127.0.0.1:18211/
python3 lab.py --safe     # the fixed version
```

The visible account page uses only this query:

```graphql
{ me { name } }
```

Send GraphQL requests as JSON to `POST /graphql`:

```json
{"query":"{ me { name } }"}
```

## Your mission

Map the query surface the interface does not advertise. Find a field that lets an ordinary,
unauthenticated caller read another user's information or an administrator-only value, then recover
the `FLAG{...}`.

## Hints — the vuln, and where to point your thinking

This is the harder tier: no step-by-step, and no solution published in this repo. Work it out — the
hints tell you the bug and where to look.

1. **The UI is only one GraphQL client.** Its query tells you what that client needs, not everything
   the server knows how to resolve.
2. **GraphQL schemas can describe themselves.** Development tools populate their field explorer
   without reading the application source. Find the meta-fields those tools ask for.
3. **Inspect the root query type and its return types.** Look for fields or arguments that expose more
   than the account screen does.
4. **Discovery and authorisation are different controls.** A field being absent from the UI—or even
   difficult to discover—does not prove its resolver checks who is calling.

When you find the right resolver, its response contains a `FLAG{...}`.

## The fix (`--safe`)

Run the fixed server on another port:

```bash
python3 lab.py --safe --port 18291
```

Replay your discovery and sensitive-data queries against it. The safe version:

- **Disables public introspection** so production callers cannot enumerate the schema.
- **Enforces authorisation inside sensitive resolvers** so knowing or guessing a field name still
  grants nothing.

The second control is the important boundary. Disabling introspection reduces exposure; resolver-level
authorisation prevents the data leak.

## Going deeper

- **Field-level access control:** apply policy to every sensitive field, not just the parent object or
  the page that normally calls it.
- **Aliases and batching:** GraphQL can request many objects in one operation, turning one broken
  object lookup into bulk extraction.
- **Query limits:** depth, complexity, pagination and rate limits help prevent expensive nested-query
  denial of service.
- **Error hygiene:** verbose type suggestions and stack traces can reveal schema details even when
  introspection is disabled.
- **The rule:** treat every resolver as an API endpoint. Authenticate, authorise and validate at the
  point where data is returned.
