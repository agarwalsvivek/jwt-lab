# Step 4: Token in memory

**Goal:** see what in-memory storage actually protects, and what it does not.

## Concept
`auth-memory.js` keeps the token in a closure variable. Nothing is written to
localStorage, so the Step 3 payload finds nothing. The cost: refresh the page and
you are logged out (real apps pair this with a refresh mechanism, often a
refresh-token cookie).

## Do
1. `python tools/jwt_tools.py reset` and use the index page's reset button
   (or `localStorage.clear()` in the console) so no old token lingers.
2. Open <http://localhost:5000/static/memory.html>, log in as alice. Refresh. You are logged out.
3. **4a: replay the Step 3 payload.**
   ```bash
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/01_steal_localstorage.txt
   ```
   Log in as alice on `memory.html?render=unsafe`. Check `loot`: you should see `LS:null`.
4. **4b: the page's own API is reachable.** Post and load this payload:
   ```bash
   python tools/jwt_tools.py reset
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/03_call_auth_global.txt
   ```
   Log in as alice, reload with `?render=unsafe`, check `loot`. You should see
   `AUTH:{"Authorization":"Bearer eyJ..."}`.
   The variable was private, but `Auth` is a global object whose `headers()` method hands out the token.
5. **4c: sniffing fetch.** Hide the global in your head (imagine you refactored it into an ES module). The
   next payload patches `window.fetch` to copy the Authorization header from future requests:
   ```bash
   python tools/jwt_tools.py reset
   python tools/jwt_tools.py comment mallory mallory-pass --file payloads/04_patch_fetch.txt
   ```
   Log in as alice, reload with `?render=unsafe`, then click **Who am I?**. Check `loot` for `SNIFFED:Bearer ...`.

## Observe
* Memory storage beats the lazy "read localStorage" payload, but only that one.
* Once attacker code runs in the page, it can call your code, wrap `fetch`, or read the DOM.

## Check yourself
1. What does memory storage genuinely improve compared with localStorage?
2. Why did payload 04 work even though the token variable is private?
3. What new problem does memory storage introduce for UX?

## Answer key
1. The token is not persisted on disk or readable by a trivial `getItem`. It dies with the tab,
   shrinking the window for theft and for leftover tokens on shared computers.
2. Because the attacker code runs with the page's privileges. Anything the legitimate code can
   do (including sending the token), injected code can observe or trigger.
3. Refresh or a new tab means re-login, so you need a silent refresh flow, typically via a
   refresh token in an HttpOnly cookie. That is exactly the BFF/cookie idea in Step 5.

**Next:** Step 5, take the token away from JavaScript entirely.
