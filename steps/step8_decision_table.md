# Step 8: Your decision table (Stop 2 checkpoint)

Fill this in from what you observed in Steps 2-7, not from memory.

| | localStorage | Memory | HttpOnly cookie |
|---|---|---|---|
| Readable by injected JS? | | | |
| Stolen token reusable off-device? | | | |
| Can XSS still act as the user while the page is open? | | | |
| Survives refresh / new tab? | | | |
| Automatically attached to requests (CSRF exposure)? | | | |
| Extra work needed | | | |
| Refresh strategy that fits | | | |
| Recommendation for **your** product | | | |

## Prompts to finish it
* If your API is on a different origin than your SPA, what changes for each column (CORS, `SameSite`, `credentials`)?
* Where would a BFF (backend-for-frontend) fit? Hint: it is the server component that holds tokens so the browser only holds a session cookie.
* What single control would have prevented Step 3 *and* Step 5b?  (Answer: not rendering untrusted HTML. Everything else is damage reduction.)

## Two-line doc to write (from your study plan)
1. How this risk appears in my app: ...
2. The mitigation I chose: ...
