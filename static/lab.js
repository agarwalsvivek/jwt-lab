// Shared React app. Uses React.createElement (no JSX / no Babel) so that the
// Content-Security-Policy step works without needing 'unsafe-eval'.
// `Auth` is provided by auth-local.js, auth-memory.js or auth-cookie.js.

const h = React.createElement;
const { useState, useEffect, useCallback } = React;

async function api(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...Auth.headers(),
      ...(options.headers || {}),
    },
  });
  let body = null;
  try {
    body = await res.json();
  } catch (e) {
    /* no JSON body */
  }
  return { ok: res.ok, status: res.status, body };
}

// ---------------------------------------------------------------------------
// The heart of the XSS lesson: three ways to render user-controlled text.
// ---------------------------------------------------------------------------
function CommentBody({ text, mode }) {
  console.log(`text: ${text}`);
  if (mode === "unsafe") {
    // DANGEROUS: React inserts this string as raw HTML.
    return h("p", { dangerouslySetInnerHTML: { __html: text } });
  }
  if (mode === "sanitized") {
    // Raw HTML allowed, but cleaned by DOMPurify first.
    return h("p", { dangerouslySetInnerHTML: { __html: DOMPurify.sanitize(text) } });
  }
  // Default: React escapes the text for us.
  return h("p", null, text);
}

function Comment({ comment, mode }) {
  return h(
    "div",
    { className: "comment" },
    h("span", { className: "author" }, comment.author),
    comment.website
      ? h("span", { className: "muted" }, " - ", h("a", { href: comment.website }, comment.website))
      : null,
    h(CommentBody, { text: comment.text, mode }),
  );
}

function App() {
  const initialMode = new URLSearchParams(window.location.search).get("render") || "safe";
  const [mode, setMode] = useState(initialMode);
  const [user, setUser] = useState(null);
  const [info, setInfo] = useState("");
  const [comments, setComments] = useState([]);
  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("alice-pass");
  const [text, setText] = useState("");
  const [website, setWebsite] = useState("");

  const refreshMe = useCallback(async () => {
    const r = await api("/api/me");
    setUser(r.ok ? r.body.user : null);
    return r;
  }, []);

  const refreshComments = useCallback(async () => {
    const r = await api("/api/comments");
    if (r.ok) setComments(r.body);
  }, []);

  useEffect(() => {
    refreshMe();
    refreshComments();
  }, []);

  async function onLogin(e) {
    e.preventDefault();
    try {
      await Auth.login(username, password);
      setInfo("Logged in.");
    } catch (err) {
      setInfo(String(err));
    }
    await refreshMe();
  }

  async function onLogout() {
    await Auth.logout();
    setInfo("Logged out.");
    await refreshMe();
  }

  async function onWhoAmI() {
    const r = await api("/api/me");
    setInfo("GET /api/me -> " + r.status + " " + JSON.stringify(r.body));
  }

  async function onPost(e) {
    e.preventDefault();
    const r = await api("/api/comments", {
      method: "POST",
      body: JSON.stringify({ text, website }),
    });
    setInfo("POST /api/comments -> " + r.status);
    if (r.ok) {
      setText("");
      setWebsite("");
    }
    await refreshComments();
  }

  return h(
    "div",
    null,
    h("h1", null, "Comments"),
    h("p", { className: "banner" }, "Token storage strategy: ", h("b", null, Auth.name)),

    h(
      "div",
      { className: "card" },
      user
        ? h(
            "div",
            null,
            "Logged in as ",
            h("b", null, user),
            " ",
            h("button", { onClick: onLogout }, "Log out"),
            h("button", { onClick: onWhoAmI }, "Who am I?"),
          )
        : h(
            "form",
            { onSubmit: onLogin },
            h("input", {
              value: username,
              onChange: (e) => setUsername(e.target.value),
              placeholder: "username",
            }),
            h("input", {
              type: "password",
              value: password,
              onChange: (e) => setPassword(e.target.value),
              placeholder: "password",
            }),
            h("button", { type: "submit" }, "Log in"),
          ),
      info ? h("pre", null, info) : null,
    ),

    h(
      "div",
      { className: "card" },
      h(
        "label",
        null,
        "Render comments as: ",
        h(
          "select",
          { value: mode, onChange: (e) => setMode(e.target.value) },
          h("option", { value: "safe" }, "safe (React escapes text)"),
          h("option", { value: "unsafe" }, "unsafe (dangerouslySetInnerHTML)"),
          h("option", { value: "sanitized" }, "sanitized (DOMPurify)"),
        ),
      ),
      h("p", { className: "muted" }, "Tip: add ?render=unsafe to the URL to start in that mode."),
    ),

    h(
      "div",
      { className: "card" },
      h(
        "form",
        { onSubmit: onPost },
        h("textarea", {
          rows: 3,
          value: text,
          onChange: (e) => setText(e.target.value),
          placeholder: "Write a comment (must be logged in)",
        }),
        h("input", {
          value: website,
          onChange: (e) => setWebsite(e.target.value),
          placeholder: "website (optional)",
          size: 40,
        }),
        h("button", { type: "submit" }, "Post"),
      ),
    ),

    h(
      "div",
      { className: "card" },
      comments.length === 0 ? h("p", { className: "muted" }, "No comments yet.") : null,
      comments.map((c) => h(Comment, { key: c.id, comment: c, mode })),
    ),
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(App));
