import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getErrorMessage } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import type { Role } from "../lib/types";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [role, setRole] = useState<Role>("CUSTOMER");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const form = new FormData(event.currentTarget);

    setError("");
    setLoading(true);

    try {
      await register({
        username: String(form.get("username")),
        email: String(form.get("email")),
        password: String(form.get("password")),
        first_name: String(form.get("first_name")),
        last_name: String(form.get("last_name")),
        role,
      });

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
        <h1>Create account</h1>
        <p className="muted">Register as a customer or vendor for local testing.</p>

        <div className="form-stack">
          {error && <div className="alert error">{error}</div>}

          <input className="input" name="first_name" placeholder="First name" required />
          <input className="input" name="last_name" placeholder="Last name" required />
          <input className="input" name="username" placeholder="Username" required />
          <input className="input" name="email" type="email" placeholder="Email" required />
          <input className="input" name="password" type="password" placeholder="Password" required />

          <select
            className="input"
            value={role}
            onChange={(event) => setRole(event.target.value as Role)}
          >
            <option value="CUSTOMER">Customer</option>
            <option value="VENDOR">Vendor</option>
          </select>

          <button className="btn" disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </div>
      </form>
    </main>
  );
}
