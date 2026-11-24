"""Backend smoke tests. Run from the project root:  python -m unittest -v"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt  # noqa: E402
import app as lab  # noqa: E402


class LabTests(unittest.TestCase):
    def setUp(self):
        lab.COMMENTS.clear(); lab.TRANSFERS.clear(); lab.LOOT.clear()
        self.client = lab.app.test_client()

    def login_token(self, user="alice", pw="alice-pass"):
        r = self.client.post("/api/login/token", json={"username": user, "password": pw})
        self.assertEqual(r.status_code, 200)
        return r.get_json()["access_token"]

    def test_token_login_and_me(self):
        token = self.login_token()
        claims = jwt.decode(token, options={"verify_signature": False})
        self.assertEqual(claims["sub"], "alice")
        r = self.client.get("/api/me", headers={"Authorization": "Bearer " + token})
        self.assertEqual(r.get_json()["user"], "alice")

    def test_bad_password_and_missing_credentials(self):
        r = self.client.post("/api/login/token", json={"username": "alice", "password": "x"})
        self.assertEqual(r.status_code, 401)
        r = self.client.post("/api/login/token", json={})
        self.assertEqual(r.status_code, 401)

    def test_tampered_token_rejected(self):
        token = self.login_token()
        header, payload, sig = token.split(".")
        bad = ".".join([header, payload[:-2] + ("AA" if payload[-2:] != "AA" else "BB"), sig])
        r = self.client.get("/api/me", headers={"Authorization": "Bearer " + bad})
        self.assertEqual(r.status_code, 401)

    def test_cookie_is_httponly_and_works(self):
        r = self.client.post("/api/login/cookie", json={"username": "alice", "password": "alice-pass"})
        self.assertEqual(r.status_code, 200)
        set_cookie = r.headers.get("Set-Cookie", "")
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("SameSite=Lax", set_cookie)
        self.assertNotIn("access_token", r.get_json())  # JS never sees the token
        r = self.client.get("/api/me")
        self.assertEqual(r.get_json()["user"], "alice")

    def test_comments_require_auth(self):
        self.assertEqual(self.client.post("/api/comments", json={"text": "hi"}).status_code, 401)
        token = self.login_token()
        r = self.client.post("/api/comments", json={"text": "hi"}, headers={"Authorization": "Bearer " + token})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get("/api/comments").get_json()[0]["author"], "alice")

    def test_attacker_collect(self):
        self.client.get("/attacker/collect?d=hello")
        self.assertEqual(self.client.get("/attacker/loot").get_json(), ["hello"])

    def test_csp_header_toggle(self):
        self.assertNotIn("Content-Security-Policy", self.client.get("/api/comments").headers)
        with mock.patch.dict(os.environ, {"LAB_CSP": "1"}):
            r = self.client.get("/api/comments")
            self.assertIn("script-src 'self'", r.headers["Content-Security-Policy"])

    def test_csrf_origin_toggle(self):
        self.client.post("/api/login/cookie", json={"username": "alice", "password": "alice-pass"})
        evil = {"Origin": "http://localhost:5001"}
        # Vulnerable by default: forged request succeeds because the cookie rides along.
        r = self.client.post("/api/transfer", data={"to": "mallory", "amount": "5"}, headers=evil)
        self.assertEqual(r.status_code, 200)
        with mock.patch.dict(os.environ, {"LAB_CSRF": "1"}):
            r = self.client.post("/api/transfer", data={"to": "mallory", "amount": "5"}, headers=evil)
            self.assertEqual(r.status_code, 403)
            same = {"Origin": "http://localhost"}  # test client host is 'localhost'
            r = self.client.post("/api/transfer", data={"to": "bob", "amount": "1"}, headers=same)
            self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
