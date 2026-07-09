import { useEffect, useState } from "react";
import { api, getErrorMessage } from "../lib/api";
import type { Cart } from "../lib/types";
import { Link } from "react-router-dom";

export function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [message, setMessage] = useState("");

  async function loadCart() {
    const response = await api.get<Cart>("/cart/");
    setCart(response.data);
  }

  useEffect(() => {
    loadCart();
  }, []);

  async function updateItem(itemId: number, quantity: number) {
    setMessage("");

    try {
      await api.patch(`/cart/items/${itemId}/`, { quantity });
      await loadCart();
    } catch (err) {
      setMessage(getErrorMessage(err));
    }
  }

  async function removeItem(itemId: number) {
    await api.delete(`/cart/items/${itemId}/remove/`);
    await loadCart();
  }

  async function clearCart() {
    await api.delete("/cart/clear/");
    await loadCart();
  }

  return (
    <main className="page">
      <div className="row">
        <div>
          <h1 className="section-title">Cart</h1>
          <p className="muted">Update quantities, remove items, and checkout.</p>
        </div>

        <Link className="btn" to="/checkout">Checkout</Link>
      </div>

      {message && <div className="alert error" style={{ marginBottom: 18 }}>{message}</div>}

      <div className="glass-card table-card">
        {!cart ? (
          "Loading cart..."
        ) : cart.items.length === 0 ? (
          <div>
            <p>Your cart is empty.</p>
            <Link className="btn" to="/products">Shop Products</Link>
          </div>
        ) : (
          <>
            <table className="table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Price</th>
                  <th>Quantity</th>
                  <th>Line Total</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>
                {cart.items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.product.name}</strong>
                      <div className="muted">{item.product.sku}</div>
                    </td>
                    <td>${item.product.price}</td>
                    <td>
                      <input
                        className="input"
                        style={{ width: 90 }}
                        type="number"
                        min={1}
                        value={item.quantity}
                        onChange={(event) =>
                          updateItem(item.id, Number(event.target.value))
                        }
                      />
                    </td>
                    <td>${item.line_total}</td>
                    <td>
                      <button className="btn danger small" onClick={() => removeItem(item.id)}>
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="row" style={{ marginTop: 20 }}>
              <button className="btn secondary" onClick={clearCart}>Clear Cart</button>
              <h2>Total: ${cart.subtotal}</h2>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
