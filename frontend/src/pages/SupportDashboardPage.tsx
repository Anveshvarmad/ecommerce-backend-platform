import { useEffect, useState } from "react";
import { api, getErrorMessage } from "../lib/api";
import type { Order } from "../lib/types";

const statusOptions = [
  "PROCESSING",
  "SHIPPED",
  "DELIVERED",
  "CANCELLED",
  "REFUNDED",
];

export function SupportDashboardPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");

  async function loadOrders() {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (status) params.set("status", status);

    const response = await api.get<Order[]>(`/backoffice/support/orders/?${params.toString()}`);
    setOrders(response.data);
  }

  useEffect(() => {
    loadOrders();
  }, []);

  async function updateStatus(orderId: number, newStatus: string) {
    setMessage("");

    try {
      await api.patch(`/backoffice/support/orders/${orderId}/status/`, {
        status: newStatus,
        note: `Updated from support dashboard to ${newStatus}.`,
      });

      setMessage("Order status updated.");
      await loadOrders();
    } catch (err) {
      setMessage(getErrorMessage(err));
    }
  }

  return (
    <main className="page">
      <h1 className="section-title">Support Dashboard</h1>
      <p className="muted">Search customer orders and manage operational status transitions.</p>

      <div className="action-bar">
        <input
          className="input"
          placeholder="Search order, customer, SKU..."
          value={q}
          onChange={(event) => setQ(event.target.value)}
          style={{ maxWidth: 360 }}
        />

        <select
          className="input"
          value={status}
          onChange={(event) => setStatus(event.target.value)}
          style={{ maxWidth: 220 }}
        >
          <option value="">All statuses</option>
          <option value="PENDING_PAYMENT">Pending Payment</option>
          <option value="PAYMENT_FAILED">Payment Failed</option>
          <option value="PAID">Paid</option>
          <option value="PROCESSING">Processing</option>
          <option value="SHIPPED">Shipped</option>
          <option value="DELIVERED">Delivered</option>
          <option value="CANCELLED">Cancelled</option>
          <option value="REFUNDED">Refunded</option>
        </select>

        <button className="btn" onClick={loadOrders}>Search</button>
      </div>

      {message && <div className="alert" style={{ marginBottom: 18 }}>{message}</div>}

      <div className="glass-card table-card">
        <table className="table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Total</th>
              <th>Move To</th>
            </tr>
          </thead>

          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td>{order.order_number}</td>
                <td>{order.user_username || "Customer"}</td>
                <td>
                  <span className="status">{order.status}</span>
                </td>
                <td>${order.total_amount}</td>
                <td>
                  <select
                    className="input"
                    defaultValue=""
                    onChange={(event) => {
                      if (event.target.value) {
                        updateStatus(order.id, event.target.value);
                        event.target.value = "";
                      }
                    }}
                  >
                    <option value="">Select status</option>
                    {statusOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}

            {orders.length === 0 && (
              <tr>
                <td colSpan={5}>No orders found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
