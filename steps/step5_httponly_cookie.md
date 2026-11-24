# Step 5: Token in an HttpOnly cookie

**Goal:** see that HttpOnly blocks token *theft* but not *abuse* from inside the victim's browser.

## Concept
`/api/login/cookie` sets `access_token` with `HttpOnly` (and `SameSite=Lax`). The browser
attaches it to same-site requests automatically and JavaScript cannot read it. The
front end (`auth-cookie.js`) never touches the token.

## Do
1. `python tools/jwt_tools.py reset`, clear browser state with the index page's reset button.
2. Open <http://localhost:5000/static/cookie.html>, log in as alice.
3. DevTools, Application/Storage, Cookies: find `access_token`. Confirm **HttpOnly** is ticked.
   Also look at Local Storage: empty.
4. In the Console run `document.cookie`. The token is not listed.
5. **5a: theft attempt.**
   ```bash
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/02_steal_cookie.txt
   ```
   Alice loads `cookie.html?render=unsafe`. `loot` should show `COOKIE:[]`.
6. **5b: abuse in place.** Attacker posts a payload that acts as the victim:
   ```bash
   python tools/jwt_tools.py reset
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/05_act_as_victim.txt
   ```
   Alice loads `?render=unsafe`. A new comment authored by **alice** appears. She never typed it.
7. **5c: data theft by proxy.**
   ```bash
   python tools/jwt_tools.py reset
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/06_read_me_endpoint.txt
   ```
   Alice loads `?render=unsafe`. `loot` shows the response of `/api/me`, fetched with her cookie.

## Observe
* The attacker cannot take the token with them (no off-device replay).
* The attacker can still perform every action the user can while the page is open, and read the responses.

## Check yourself
1. What exactly does HttpOnly protect against?
2. If XSS can still act as the user, why prefer HttpOnly cookies at all?
3. Which cookie attributes should a production auth cookie have?

## Answer key
1. Reading the cookie's value from JavaScript (`document.cookie`), so the credential cannot be exfiltrated and reused elsewhere.
2. It limits the damage window to "while the victim's page is open" and removes the portable
   credential, which makes attacks noisier, less scalable and easier to contain (rotate, revoke, rate limit).
   It is damage reduction, not a fix for XSS.
3. `HttpOnly`, `Secure` (HTTPS only; this lab sets it false because it runs on plain http),
   `SameSite` (Lax or Strict), a tight `Path`/scope, and a short lifetime. Consider the `__Host-` prefix;
   I'm fairly sure it requires Secure, Path=/ and no Domain, but verify against MDN before relying on it.

**Next:** Step 6, fix the root cause: XSS in React.
