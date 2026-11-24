"""JWT storage + XSS lab backend.

INTENTIONALLY VULNERABLE - FOR LEARNING ONLY.
Run on localhost only. Never deploy this.

Toggles (environment variables, read on every request):
  LAB_CSP=1   send a Content-Security-Policy header   (Step 6)
  LAB_CSRF=1  reject cross-origin state-changing requests via Origin check (Step 7)
"""
import datetime
import os

import jwt
from flask import Flask, abort, jsonify, request

app = Flask(__name__, static_folder="static", static_url_path="/static")

JWT_SECRET = "lab-only-secret-lab-only-secret-1234"  # 32+ bytes; never hard-code a secret in real code
JWT_ALG = "HS256"
TOKEN_MINUTES = 15

# Plain-text passwords: lab only. Real apps store salted password hashes.
USERS = {"alice": "alice-pass", "mallory": "mallory-pass"}

COMMENTS = []   # in-memory "database"
TRANSFERS = []
LOOT = []       # what the simulated attacker collected


# ---------------------------------------------------------------- helpers
def make_token(username):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def current_claims():
    """Return verified JWT claims, or None.

    Accepts the token from an Authorization header (localStorage / memory
    strategies) OR from the access_token cookie (cookie strategy).
    """
    token = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[len("Bearer "):]
    elif "access_token" in request.cookies:
        token = request.cookies["access_token"]
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.InvalidTokenError:
        return None


def require_user():
    claims = current_claims()
    if claims is None:
        abort(401)
    return claims["sub"]


def check_credentials():
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not username or USERS.get(username) != password:
        return None
    return username


# ------------------------------------------------------- global behaviour
@app.before_request
def csrf_origin_check():
    """Step 7 fix: block state-changing requests coming from another origin."""
    if os.environ.get("LAB_CSRF") != "1":
        return
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        origin = request.headers.get("Origin")
        if origin and origin != request.host_url.rstrip("/"):
            abort(403, description="Cross-origin request blocked")


@app.after_request
def add_security_headers(resp):
    """Step 6: Content-Security-Policy, only when LAB_CSP=1."""
    if os.environ.get("LAB_CSP") == "1":
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com; "
            "object-src 'none'; "
            "base-uri 'none'"
        )
    return resp


@app.errorhandler(401)
def unauthorized(_e):
    return jsonify({"error": "unauthorized"}), 401


# ------------------------------------------------------------------ pages
@app.get("/")
def index():
    return app.send_static_file("index.html")


# ------------------------------------------------------------------- auth
@app.post("/api/login/token")
def login_token():
    """Strategies A and B: token is returned in the JSON body."""
    user = check_credentials()
    if user is None:
        return jsonify({"error": "bad credentials"}), 401
    return jsonify({"access_token": make_token(user), "token_type": "Bearer"})


@app.post("/api/login/cookie")
def login_cookie():
    """Strategy C: token is set as an HttpOnly cookie, never shown to JS."""
    user = check_credentials()
    if user is None:
        return jsonify({"error": "bad credentials"}), 401
    resp = jsonify({"ok": True, "user": user})
    resp.set_cookie(
        "access_token",
        make_token(user),
        httponly=True,        # JavaScript cannot read it
        samesite="Lax",       # Step 7 explores what this does and does not stop
        secure=False,         # must be True on HTTPS in real life
        max_age=TOKEN_MINUTES * 60,
        path="/",
    )
    return resp


@app.post("/api/logout")
def logout():
    resp = jsonify({"ok": True})
    resp.delete_cookie("access_token", path="/")
    return resp


@app.get("/api/me")
def me():
    claims = current_claims()
    if claims is None:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"user": claims["sub"], "expires_at": claims["exp"]})


# --------------------------------------------------------------- comments
@app.get("/api/comments")
def list_comments():
    return jsonify(COMMENTS)


@app.post("/api/comments")
def add_comment():
    user = require_user()
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))[:2000]
    website = str(data.get("website", ""))[:500]
    # VULNERABILITY (on purpose): we store whatever the user sends.
    COMMENTS.append(
        {"id": len(COMMENTS) + 1, "author": user, "text": text, "website": website}
    )
    return jsonify({"ok": True}), 201


# -------------------------------------------------------------- transfers
@app.post("/api/transfer")
def transfer():
    """Cookie-authenticated, form-encoded: the classic CSRF target (Step 7)."""
    user = require_user()
    to = request.values.get("to", "")
    amount = request.values.get("amount", "")
    TRANSFERS.append({"from": user, "to": to, "amount": amount})
    return jsonify({"ok": True, "from": user, "to": to, "amount": amount})


@app.get("/api/transfers")
def list_transfers():
    require_user()
    return jsonify(TRANSFERS)


# ---------------------------------------------------------- lab utilities
@app.post("/api/reset")
def reset():
    COMMENTS.clear()
    TRANSFERS.clear()
    LOOT.clear()
    return jsonify({"ok": True})


# ---------------------------------------------- simulated attacker server
# In real life this would be a different origin, e.g. https://evil.example.
# It lives here only so the lab needs a single process.
@app.get("/attacker/collect")
def attacker_collect():
    data = request.args.get("d", "")
    LOOT.append(data)
    print(f"[ATTACKER] collected: {data}", flush=True)
    return "", 204


@app.get("/attacker/loot")
def attacker_loot():
    return jsonify(LOOT)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
