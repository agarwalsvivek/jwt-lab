// Strategy C: the server sets an HttpOnly cookie; JavaScript never sees the JWT.
const Auth = {
  name: "HttpOnly cookie",

  async login(username, password) {
    const res = await fetch("/api/login/cookie", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error("Login failed (" + res.status + ")");
    // Nothing to store: the browser keeps the cookie and attaches it for us.
  },

  headers() {
    return {}; // no Authorization header needed
  },

  async logout() {
    await fetch("/api/logout", { method: "POST" });
  },
};
