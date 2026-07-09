import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, getErrorMessage } from "../lib/api";
import type { Cart } from "../lib/types";

export function CheckoutPage() {
  const navigate = useNavigate();

  const [cart, setCart] = useState<Cart | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadCart() {
    const response = await api.get<Cart>("/cart/");
    setCart(response.data);
  }

  useEffect(() => {
    loadCart();
  }, []);

  async function checkout(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const form = new FormData(event.currentTarget);

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/orders/checkout/", {
        shipping_address: {
          full_name: String(form.get("full_name")),
          line1: String(form.get("line1")),
          line2: String(form.get("line2")),
          city: String(form.get("city")),
          state: String(form.get("state")),
          postal_code: String(form.get("postal_code")),
          country: String(form.get("country")),
        },
        notes: String(form.get("notes")),
      });

      navigate(`/orders?created=${response.data.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <h1 className="section-title">Checkout</h1>

      <div className="checkout-grid">
        <form className="glass-card table-card form-stack" onSubmit={checkout}>
          {error && <div className="alert error">{error}</div>}

          <input className="input" name="full_name" placeholder="Full name" defaultValue="Test Customer" required />
          <input className="input" name="line1" placeholder="Address line 1" defaultValue="123 Main Street" required />
          <input className="input" name="line2" placeholder="Address line 2" defaultValue="Apt 4B" />
          <input className="input" name="city" placeholder="City" defaultValue="Jersey City" required />
          <input className="input" name="state" placeholder="State" defaultValue="NJ" required />
          <input className="input" name="postal_code" placeholder="Postal code" defaultValue="07302" required />
          <input className="input" name="country" placeholder="Country" defaultValue="USA" required />
          <textarea className="input" name="notes" placeholder="Order notes" />

          <button className="btn" disabled={loading}>
            {loading ? "Creating order..." : "Place Order"}
          </button>
        </form>

        <aside className="glass-card table-card">
          <h2>Order Summary</h2>

          {!cart ? (
            <p>Loading...</p>
          ) : (
            <>
              <p className="muted">Items: {cart.total_items}</p>
              <h1>${cart.subtotal}</h1>
              <p className="muted">
                Tax and shipping will be calculated by the backend during checkout.
              </p>
            </>
          )}
        </aside>
      </div>
    </main>
  );
}
