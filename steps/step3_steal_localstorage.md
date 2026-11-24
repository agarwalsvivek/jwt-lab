# Step 3: Stored XSS steals the localStorage token

**Goal:** run a complete attack: inject, execute, exfiltrate, replay.

## Concept
The server stores comments exactly as submitted. If the front end renders them
with `dangerouslySetInnerHTML`, an attacker's HTML becomes live DOM in the
victim's browser. Scripts inserted via `innerHTML` do not run, but event
handlers such as `onerror` on an `<img>` do.

Look at `CommentBody` in `static/lab.js`: three modes, `safe` is the default.

## Do
1. `python tools/jwt_tools.py reset`
2. **Attacker (mallory)** posts the payload from the command line:
   ```bash
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/01_steal_localstorage.txt
   ```
   Read the payload first: `cat payloads/01_steal_localstorage.txt`
3. **Victim (alice)**: open <http://localhost:5000/static/local.html> and log in as alice.
   You will see the payload displayed as **harmless text**. That is React's default escaping.
4. Switch the dropdown to **unsafe (dangerouslySetInnerHTML)**, or open
   <http://localhost:5000/static/local.html?render=unsafe>.
   The broken image fires `onerror`. (Log in first and then reload; otherwise there is no token to steal yet.)
5. **Attacker's view:** `python tools/jwt_tools.py loot` or open <http://localhost:5000/attacker/loot>.
   You should see `LS:eyJ...` and the Flask terminal prints `[ATTACKER] collected: ...`.
6. **Replay** the stolen token from a different "machine" (your terminal):
   ```bash
   python tools/jwt_tools.py me <STOLEN_TOKEN>
   ```
   You are now alice, with no browser involved.
7. Try the script-tag payload and compare:
   ```bash
   python tools/jwt_tools.py reset
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/07_script_tag.txt
   ```
   Reload in unsafe mode. Check `loot`. (Expected: nothing.)

## Observe
* Safe mode: nothing happens. Unsafe mode: token stolen.
* The stolen token works off-device until it expires (15 minutes here).
* `<script>` inserted through `innerHTML` does not execute, but `onerror` does. Blocking `<script>` is not a defence.

## Check yourself
1. Which line of code is the actual vulnerability?
2. Why did the exfiltration need no special permission from the browser?
3. If the token lasted 15 minutes, why is this still serious?

## Answer key
1. `dangerouslySetInnerHTML: { __html: text }` in `CommentBody`, combined with the server
   storing and returning untrusted text. The root cause is rendering untrusted HTML.
2. The payload runs in alice's page, on the app's own origin, so `fetch` and `localStorage`
   are fully allowed. In this lab the attacker server is the same origin; against a real
   different origin, `fetch` would still send the request (a request to another site is allowed;
   it is reading the *response* that CORS controls), unless CSP `connect-src` blocks it.
3. The attacker can use the token immediately, can chain it to change account details or
   obtain longer-lived access, and XSS can steal a fresh token every time the victim visits.

**Next:** Step 4, take the token out of storage.
