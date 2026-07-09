import { useEffect, useState } from "react";
import { api, getErrorMessage } from "../lib/api";
import type { Order } from "../lib/types";

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [message, setMessage] = useState("");

  async function loadOrders() {
    const response = await api.get<Order[]>("/orders/");
    setOrders(response.data);
  }

  useEffect(() => {
    loadOrders();
  }, []);

  async function pay(order: Order) {
    setMessage("");

    try {
      await api.post("/payments/initiate/", {
        order_id: order.id,
        idempotency_key: `frontend-${order.id}-${Date.now()}`,
        force_outcome: "SUCCESS",
      });

      setMessage(`Payment successful for ${order.order_number}.`);
      await loadOrders();
    } catch (err) {
      setMessage(getErrorMessage(err));
    }
  }

  return (
    <main className="page">
      <h1 className="section-title">Orders</h1>
      <p className="muted">View orders and simulate fake payment success.</p>

      {message && <div className="alert" style={{ marginBottom: 18 }}>{message}</div>}

      <div className="glass-card table-card">
        <table className="table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Status</th>
              <th>Total</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td>{order.order_number}</td>
                <td>
                  <span className="status">{order.status}</span>
                </td>
                <td>${order.total_amount}</td>
                <td>{new Date(order.created_at).toLocaleString()}</td>
                <td>
                  {["PENDING_PAYMENT", "PAYMENT_FAILED"].includes(order.status) && (
                    <button className="btn small" onClick={() => pay(order)}>
                      Pay Now
                    </button>
                  )}
                </td>
              </tr>
            ))}

            {orders.length === 0 && (
              <tr>
                <td colSpan={5}>No orders yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
