# Step 6: XSS in React: defaults, escape hatches, sanitizing, CSP

**Goal:** understand why React is safe by default, the escape hatches that break that,
and two layers of defence (sanitize, CSP).

## Concept
* `h("p", null, text)` (JSX `{text}`): React sets text content, so HTML is shown literally. Safe by default.
* `dangerouslySetInnerHTML`: you opt in to raw HTML. The name is the warning.
* Other risky spots: `href`/`src` values from users (e.g. `javascript:` URLs), rendering
  HTML from markdown or a CMS, `innerHTML`/`document.write` in effects, third-party widgets.
* Defence in depth: sanitize with DOMPurify, and add a CSP that blocks inline script and handlers.

## Do
### 6a: three modes, one payload
```bash
python tools/jwt_tools.py reset
python tools/jwt_tools.py comment mallory mallory-pass --file payloads/01_steal_localstorage.txt
```
Log in as alice on `local.html` and cycle the dropdown: `safe`, `unsafe`, `sanitized`.
After each switch, check `loot`. Only `unsafe` should add an entry. In `sanitized` mode, inspect the
element in DevTools (Elements tab): DOMPurify keeps the `<img>` but removes the `onerror` attribute.

### 6b: the `javascript:` URL
```bash
python tools/jwt_tools.py comment mallory mallory-pass --text "click my site" --website "javascript:fetch('/attacker/collect?d=JSURL_CLICKED')"
```
In `safe` mode, click the website link as alice and check `loot` and the browser console. React 18 logs
a warning about `javascript:` URLs. I am not certain whether your React version blocks them or only warns, so
treat the result you see as the fact for this version, and check the React docs/release notes before relying on it.
The fix is to validate on the server and/or client: only allow `http:` and `https:` schemes.

### 6c: add a CSP
Stop the server (Ctrl+C) and restart it with the policy on:
```bash
LAB_CSP=1 python app.py
```
Hard-refresh `local.html?render=unsafe` as alice (payload 01 still stored; if not, repost it). Open the
Console: you should see a violation about refusing to execute an inline event handler, and `loot`
stays empty even in unsafe mode. Look at the policy in `add_security_headers` in `app.py`.
If React or DOMPurify fail to load under the policy, tell me what the console says; I could not run a
browser in my environment to verify the CDN scripts load with this exact policy.

### 6d: audit exercise
```bash
grep -rn "dangerouslySetInnerHTML" static/
```
For each hit decide: is the data trusted? Is it sanitized? Is there a test? Then write a regression test idea,
for example: render a component with `<img src=x onerror=...>` through the sanitizer and assert the output
contains no `onerror` attribute.

### 6e: Trusted Types (read-only for now)
Research the CSP directive `require-trusted-types-for 'script'`, which makes the browser
reject string assignments to sinks like `innerHTML`. Browser support is not universal, so check
current support tables (for example MDN) before depending on it.

## Observe
* Same stored payload, three outcomes depending only on how the front end renders it.
* CSP can neutralise an XSS bug even when the bug exists, but it is a second layer, not a licence to keep the bug.

## Check yourself
1. Why did the `safe` mode need no sanitizer?
2. Why is sanitizing at render time better than "clean it when it is saved"?
3. What does the CSP stop in 6c, and what can it not stop?
4. Name two places besides `dangerouslySetInnerHTML` where untrusted data can become code.

## Answer key
1. React turns the string into a text node, so markup is never parsed.
2. The correct encoding depends on the output context (HTML body, attribute, URL, JS). Storing raw
   data and encoding or sanitizing on output keeps you correct per context, and sanitizer rules improve over time.
   Validating on input is still useful as an extra layer.
3. It blocks inline event handlers and scripts from non-allowed sources, so the injected `onerror` never runs.
   It does not fix logic bugs such as injected links to phishing sites, HTML injection that only changes
   appearance, or abuse that uses allowed scripts.
4. `javascript:` URLs in `href`, attacker-controlled `src` for scripts/iframes, `innerHTML` in effects or refs,
   server-side rendering that injects unescaped JSON into a `<script>` block, and vulnerable third-party libraries.

**Next:** Step 7 (bonus), the cost of cookies: CSRF.
