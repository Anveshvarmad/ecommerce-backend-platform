import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getErrorMessage } from "../lib/api";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("customer1");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(username, password);
      navigate("/products");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <form className="glass-card form-card" onSubmit={onSubmit}>
        <h1>Welcome back</h1>
        <p className="muted">Login with customer1 / Password123! for testing.</p>

        <div className="form-stack">
          {error && <div className="alert error">{error}</div>}

          <input
            className="input"
            placeholder="Username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />

          <input
            className="input"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <button className="btn" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>

          <p className="muted">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </form>
    </main>
  );
}
