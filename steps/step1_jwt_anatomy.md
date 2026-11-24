# Step 1: Anatomy of a JWT (no browser yet)

**Goal:** see that a JWT is three base64url parts, readable by anyone, protected
by a signature rather than secrecy.

## Concept

`header.payload.signature`. The header and payload are just base64url-encoded
JSON. The signature (here HMAC-SHA256 with the server's secret) lets the server
detect tampering. It does **not** hide the contents.

## Do

1. Start the server: `python app.py`
2. In a second terminal (same venv) get a token:
   ```bash
   python tools/jwt_tools.py login alice alice-pass
   ```
   Copy the long string it prints.
3. Decode it (no secret needed):
   ```bash
   python tools/jwt_tools.py decode <TOKEN>
   ```
4. Use it:
   ```bash
   python tools/jwt_tools.py me <TOKEN>
   ```
5. Tamper with it. This changes `sub` from `alice` to `mallory` but keeps the old signature:
   ```bash
   python tools/jwt_tools.py tamper <TOKEN>
   python tools/jwt_tools.py me <TAMPERED_TOKEN>
   ```
6. Open `app.py` and find `make_token` and `current_claims`. Note `exp`
   (15 minutes) and `algorithms=[JWT_ALG]` in the decode call.

7. All in one
   ```bash
   T=$(python tools/jwt_tools.py login alice alice-pass)
   python tools/jwt_tools.py decode "$T"          # signature should say 32 bytes
   python tools/jwt_tools.py me "$T"              # should be 200 and alice
   python tools/jwt_tools.py me "$(python tools/jwt_tools.py tamper "$T")"   # should be 401
   ```

## Observe

- Step 3 shows `sub`, `iat`, `exp` in plain text.
- Step 5 returns `401`.

## Check yourself

1. Can someone who steals the token read its claims? Can they change them?
2. Why does `current_claims` pass `algorithms=[JWT_ALG]` instead of trusting the header?
3. If the token cannot be forged, why does _where you store it_ still matter?

## Answer key

1. Yes, they can read it. No, they cannot change it without the secret.
2. Otherwise an attacker could pick the algorithm (historically `none` or
   RS/HS confusion attacks). Pin the allowed algorithm on the server.
3. A stolen valid token works for anyone until it expires. The signature proves
   the token is genuine, not that the person presenting it is the real user.
