// Strategy B: keep the JWT only in a JavaScript variable (lost on refresh).
// The variable is hidden inside a closure, but note that `Auth` itself is a
// global name - Step 4 shows why that still matters.
const Auth = (function () {
  let accessToken = null;

  return {
    name: "memory (JS variable)",

    async login(username, password) {
      const res = await fetch("/api/login/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error("Login failed (" + res.status + ")");
      const data = await res.json();
      accessToken = data.access_token;
    },

    headers() {
      return accessToken ? { Authorization: "Bearer " + accessToken } : {};
    },

    async logout() {
      accessToken = null;
    },
  };
})();
