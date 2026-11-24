# Step 2: Token in localStorage

**Goal:** understand exactly where the token lives and how the app sends it.

## Concept
`auth-local.js` stores the token with `localStorage.setItem` and `lab.js` adds an
`Authorization: Bearer ...` header to each API call. localStorage is readable by
**any JavaScript running on your origin**: your code, your npm dependencies,
analytics snippets, and injected XSS.

## Do
1. `python tools/jwt_tools.py reset`, then open <http://localhost:5000/static/local.html>
2. Log in as `alice` / `alice-pass`.
3. Open DevTools:
   * **Application** (Chrome/Edge) or **Storage** (Firefox) tab, then Local Storage, `http://localhost:5000`.
     Find `access_token`.
   * **Network** tab: click "Who am I?" and inspect the request headers for `Authorization`.
4. Refresh the page. You stay logged in. Open the page in a second tab. Still logged in.
5. In the DevTools **Console**, run:
   ```js
   localStorage.getItem("access_token")
   ```
6. Post a comment as alice and notice it renders as plain text.

## Observe
* The token survives refresh and is shared across tabs.
* Any code you type in the console can read it, and so can any script on the page.

## Check yourself
1. Name three kinds of code that can run on your origin and read localStorage.
2. What is the user-experience upside of this strategy?
3. Does this strategy need CSRF protection? Why or why not?

## Answer key
1. Your own bundle, third-party npm dependencies, third-party scripts (analytics, chat widgets, tag managers),
   browser extensions with page access, and any injected script from an XSS bug.
2. Simple to implement, survives refresh, works across tabs, works easily with APIs on other origins.
3. Not for the usual cookie-based CSRF. The browser does not attach the token
   automatically, so a forged cross-site request has no credentials. (Step 7 shows the cookie side of this.)

**Next:** Step 3 turns the "any JavaScript can read it" point into a working attack.
