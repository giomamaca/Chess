import { useState } from "react";
import BASE_URL from "../config";
import {Screen} from "../types"

interface Props {
  setLoggedIn: (value: boolean) => void;
  setScreen: (screen: Screen) => void;
  styles: string;
}

export default function LogRegistration({ setLoggedIn, setScreen, styles }: Props) {
  const [authScreen, setAuthScreen] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ username: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const authStyles = `
    .auth-root {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: radial-gradient(ellipse at 50% 0%, #1a1208 0%, #0d0d0d 70%);
      padding: 2rem 1rem;
      position: relative;
      overflow: hidden;
    }
    .auth-root::before {
      content: '';
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(212,175,55,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(212,175,55,0.03) 1px, transparent 1px);
      background-size: 60px 60px;
      pointer-events: none;
    }
    .auth-card {
      background: #111;
      border: 1px solid #2a2a2a;
      padding: 2.8rem 2.4rem;
      width: 100%;
      max-width: 380px;
      box-shadow: 0 0 80px rgba(0,0,0,0.9), 0 0 1px #c9a84c44;
      position: relative;
      clip-path: polygon(12px 0%, 100% 0%, calc(100% - 12px) 100%, 0% 100%);
    }
    .auth-tabs {
      display: flex;
      border-bottom: 1px solid #2a2a2a;
      margin-bottom: 2rem;
    }
    .auth-tab {
      flex: 1;
      background: none;
      border: none;
      padding: 0.7rem;
      font-family: 'Cinzel', serif;
      font-size: 0.65rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: #444;
      cursor: pointer;
      transition: color 0.25s;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
    }
    .auth-tab:hover { color: #888; }
    .auth-tab.active {
      color: #d4af37;
      border-bottom-color: #d4af37;
    }
    .auth-field { margin-bottom: 1.2rem; }
    .auth-label {
      display: block;
      font-family: 'Cinzel', serif;
      font-size: 0.6rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: #555;
      margin-bottom: 0.45rem;
    }
    .auth-input {
      width: 100%;
      background: #080808;
      border: 1px solid #222;
      padding: 0.7rem 0.9rem;
      color: #e8dcc8;
      font-size: 1rem;
      font-family: 'Crimson Text', serif;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      box-sizing: border-box;
    }
    .auth-input::placeholder { color: #333; }
    .auth-input:focus {
      border-color: #d4af37;
      box-shadow: 0 0 0 3px rgba(212,175,55,0.08);
    }
    .auth-error {
      font-family: 'Crimson Text', serif;
      font-style: italic;
      font-size: 0.9rem;
      color: #c0392b;
      text-align: center;
      min-height: 1.2em;
      margin-bottom: 1rem;
    }
    .auth-divider {
      border: none;
      border-top: 1px solid #1a1a1a;
      margin: 1.6rem 0;
    }
    .auth-switch {
      text-align: center;
      font-family: 'Crimson Text', serif;
      font-style: italic;
      font-size: 0.95rem;
      color: #555;
    }
    .auth-switch button {
      background: none;
      border: none;
      color: #d4af37;
      cursor: pointer;
      font-family: 'Crimson Text', serif;
      font-style: italic;
      font-size: 0.95rem;
      padding: 0;
      text-decoration: underline;
    }
  `;

  const handleDataResult = async (api: string) => {
      const res = await fetch(`${BASE_URL}/auth/${api}`, {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "ngrok-skip-browser-warning": "true",
          },
          body: JSON.stringify({
              username: form.username,
              password: form.password,
          }),
      });
      const data = await res.json();
      return data;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!form.username.trim() || !form.password) {
      setError("All fields are required.");
      return;
    }
    if (authScreen === "register" && form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const api = authScreen === "login" ? "login" : "register";
      const data = await handleDataResult(api);
      if (data.success) {
          localStorage.setItem("name", form.username);
          setLoggedIn(true);
          setScreen("menu");
      } else {
          setError(data.detail || "Invalid credentials. Please try again.");
          setForm({ username: "", password: "", confirm: "" });
      }
    } catch (err: any) {
      setError(err?.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const switchScreen = (s: "login" | "register") => {
    setAuthScreen(s);
    setError("");
    setForm({ username: "", password: "", confirm: "" });
  };

  return (
    <>
      <style>{styles}</style>
      <style>{authStyles}</style>

      <div className="auth-root fade-in">
        <div className="chess-crown">♛</div>
        <h1 className="game-title">REGICIDE</h1>
        <p className="game-subtitle">A Chess Experience</p>
        <div className="divider" />

        <div className="auth-card">
          <div className="auth-tabs">
            <button
              className={`auth-tab ${authScreen === "login" ? "active" : ""}`}
              onClick={() => switchScreen("login")}
            >
              Sign In
            </button>
            <button
              className={`auth-tab ${authScreen === "register" ? "active" : ""}`}
              onClick={() => switchScreen("register")}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="auth-field">
              <label className="auth-label">Username</label>
              <input
                className="auth-input"
                type="text"
                placeholder="Enter username"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                autoFocus
              />
            </div>
            <div className="auth-field">
              <label className="auth-label">Password</label>
              <input
                className="auth-input"
                type="password"
                placeholder="Enter password"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              />
            </div>

            {authScreen === "register" && (
              <div className="auth-field">
                <label className="auth-label">Confirm Password</label>
                <input
                  className="auth-input"
                  type="password"
                  placeholder="Repeat password"
                  value={form.confirm}
                  onChange={e => setForm(f => ({ ...f, confirm: e.target.value }))}
                />
              </div>
            )}

            <div className="auth-error">{error}</div>

            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading}
              style={{ width: "100%", textAlign: "center" }}
            >
              {loading ? "…" : authScreen === "login" ? "Log In" : "Create Account"}
            </button>
          </form>

          <hr className="auth-divider" />
          <p className="auth-switch">
            {authScreen === "login" ? (
              <>No account?{" "}
                <button onClick={() => switchScreen("register")}>Register here</button>
              </>
            ) : (
              <>Already registered?{" "}
                <button onClick={() => switchScreen("login")}>Sign in</button>
              </>
            )}
          </p>
        </div>
      </div>
    </>
  );
}