# Step 7 (bonus): CSRF and SameSite, the price of cookies

**Goal:** see that cookie auth is attached automatically, so other sites can trigger authenticated
requests, and learn what `SameSite` does and does not cover.

## Concept
`/api/transfer` accepts form-encoded POSTs and authenticates via the cookie, a classic CSRF
target. `SameSite=Lax` stops cookies on most cross-**site** POSTs. But "site" is scheme + registrable
domain and **ignores the port**, so `localhost:5001` counts as the *same site* as `localhost:5000`.
The lab uses that to model a same-site-but-different-origin attacker (think a vulnerable sibling
subdomain). Cross-site behaviour depends on browser details, so treat what you observe as the ground truth.

## Do
1. Restart the normal server (`python app.py`, no CSP flag), clear state, open
   <http://localhost:5000/static/cookie.html> and log in as alice (cookie strategy).
2. In a second terminal, serve the attacker page on port 5001:
   ```bash
   python -m http.server 5001 --directory attacker
   ```
3. In the same browser, visit <http://localhost:5001/csrf.html>. It auto-submits a hidden form to
   `http://localhost:5000/api/transfer`.
4. Check the damage: on `cookie.html` use the console:
   ```js
   fetch("/api/transfers").then(r => r.json()).then(console.log)
   ```
   You should see a transfer from alice to mallory that alice never made. (If you see 401 or nothing,
   your browser did not send the cookie; note that and tell me what you saw.)
5. **Fix it.** Stop the lab server, restart with the Origin check:
   ```bash
   LAB_CSRF=1 python app.py
   ```
   Log in again, repeat step 3. The response is `403` and no new transfer is recorded.
   Read `csrf_origin_check` in `app.py`.
6. **Compare strategies.** On `local.html` (Bearer header), would the same forged form work? Why not?

## Observe
* A forged request rides on the victim's cookie, with no XSS needed.
* Bearer-header strategies are immune to this style of attack because the browser does not add the header automatically.

## Check yourself
1. Why does a hidden form from another origin work against cookie auth?
2. What does `SameSite` protect, and what did the port example reveal?
3. Name two other CSRF defences besides the Origin check.

## Answer key
1. The browser attaches cookies based on the *destination*, not on who initiated the request.
2. It restricts when cookies go along on cross-site requests. It does not separate different origins within the
   same site (ports, subdomains), so same-site attackers still need other defences.
3. Anti-CSRF tokens (synchroniser or double-submit), requiring a custom header or JSON content type on
   state-changing endpoints (with CORS preflight protection), and checking `Sec-Fetch-Site`. Verify exact
   current guidance in the OWASP CSRF Prevention Cheat Sheet.
