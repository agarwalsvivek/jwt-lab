# JWT storage + XSS in React: hands-on lab

A small Python (Flask) + React lab for two topics from your study plan:
**"JWT storage: localStorage, memory, HttpOnly cookie"** and **"XSS in React"**.

> **Intentionally vulnerable. Run on localhost only. Never deploy it.**

## Setup

These instructions are for **WSL2 (Ubuntu)**. Run every command in the WSL
terminal, not in PowerShell or CMD. You need Python 3.9+ and a browser with
internet access (React and DOMPurify load from the unpkg CDN).

One-time setup. Ubuntu leaves out `venv` by default, and it uses `python3`
instead of `python`:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Keep the project in the Linux filesystem (for example `~/Projects/...`), not
under `/mnt/c/...`, because file access there is much slower.

```bash
cd ~/Projects/auth/jwt-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py                      # http://localhost:5000
```

Once the venv is active, `python` refers to the venv's Python 3, so the rest of
the lab uses `python`. Run `source .venv/bin/activate` again in each new WSL
terminal.

Open the lab in your normal **Windows browser** at `http://localhost:5000`.
WSL2 forwards `localhost` to Windows automatically. If the page does not load:

* make sure Flask is listening (the terminal shows `Running on http://127.0.0.1:5000`);
* run `wsl --shutdown` in PowerShell, then reopen the WSL terminal and try again;
* as a last resort, temporarily change `host="127.0.0.1"` to `host="0.0.0.0"`
  at the bottom of `app.py` and browse to the IP that `hostname -I` prints. This
  exposes the app to your network, which is risky because it is intentionally
  vulnerable. Change it back afterwards.

Optional check of the backend (in a second WSL terminal, after activating the venv):

```bash
python -m unittest discover -s tests -v
```

Always use `http://localhost:5000` (not `127.0.0.1`) so cookies and the Origin
check behave the same in every step.

If files copied from Windows show up with `:Zone.Identifier` twins, remove them with:

```bash
find . -name '*:Zone.Identifier' -type f -delete
```

## How to work through it

Do **one step at a time**, in order. Each file in `steps/` has the same shape:
goal, concept, do, observe, check-yourself questions, answer key (try first!).

| Step | Topic | You will see |
|------|-------|--------------|
| 1 | Anatomy of a JWT | A token is signed, not secret |
| 2 | Token in localStorage | Where it lives, how it is sent |
| 3 | Stored XSS steals the localStorage token | The core risk, end to end |
| 4 | Token in memory | What it fixes, what it does not |
| 5 | Token in an HttpOnly cookie | Theft blocked, abuse still possible |
| 6 | XSS in React: defaults, escape hatches, sanitizing, CSP | The real fix is upstream |
| 7 | Bonus: CSRF and SameSite | The price of cookies |
| 8 | Decision table | Your Stop 2 checkpoint |

## Project map

```
app.py                 Flask backend (login, comments, transfer, attacker collector)
static/local.html      Strategy A  (auth-local.js)
static/memory.html     Strategy B  (auth-memory.js)
static/cookie.html     Strategy C  (auth-cookie.js)
static/lab.js          Shared React app (comment rendering lives in CommentBody)
payloads/              XSS payloads you will post as the attacker
tools/jwt_tools.py     CLI: login, decode, tamper, me, comment, loot, reset
attacker/              Simulated attacker site for Step 7
steps/                 The guides
```

## Useful commands

```bash
python tools/jwt_tools.py reset    # clear comments + attacker loot between steps
python tools/jwt_tools.py loot     # see what the attacker collected
```
The index page also has a button that clears localStorage and the cookie.
The server accepts a Bearer header **or** the cookie, so log out before you
switch strategies.

## Things worth knowing up front

* The "attacker server" is a route on the same Flask app, only so you need one
  process. In real life it would be another origin.
* The pages use `React.createElement` instead of JSX so Step 6's
  Content-Security-Policy works without `'unsafe-eval'`.
* React is pinned to major version 18 on purpose; I believe React 19 no longer
  ships UMD builds, but verify that in the React release notes if you change it.
* Real apps should pin exact CDN versions and use Subresource Integrity, or
  better, bundle dependencies (this is your Stop 10 topic).
