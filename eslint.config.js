// ESLint flat config.
// The browser code here is loaded with plain <script> tags (no bundler, no
// modules), so files share globals: React/ReactDOM/DOMPurify come from the CDN
// and `Auth` is defined by whichever auth-*.js page script is loaded.
const js = require("@eslint/js");
const globals = require("globals");
const prettier = require("eslint-config-prettier");

module.exports = [
  { ignores: [".venv/**", "node_modules/**"] },

  js.configs.recommended,

  {
    files: ["static/**/*.js", "attacker/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: {
        ...globals.browser,
        React: "readonly",
        ReactDOM: "readonly",
        DOMPurify: "readonly",
        Auth: "readonly",
      },
    },
    rules: {
      "no-unused-vars": ["error", { caughtErrors: "none" }],
    },
  },

  {
    // Each auth-*.js defines the global `Auth` that lab.js consumes.
    files: ["static/auth-*.js"],
    languageOptions: { globals: { Auth: "off" } },
    rules: {
      "no-unused-vars": ["error", { varsIgnorePattern: "^Auth$", caughtErrors: "none" }],
    },
  },

  {
    files: ["eslint.config.js"],
    languageOptions: { sourceType: "commonjs", globals: globals.node },
  },

  // Must be last: turns off stylistic rules that conflict with Prettier.
  prettier,
];
