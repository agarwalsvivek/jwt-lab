// Strategy A: keep the JWT in localStorage and send it as a Bearer header.
const Auth = {
  name: "localStorage",

  async login(username, password) {
    const res = await fetch("/api/login/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error("Login failed (" + res.status + ")");
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
  },

  headers() {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: "Bearer " + token } : {};
  },

  async logout() {
    localStorage.removeItem("access_token");
  },
};
