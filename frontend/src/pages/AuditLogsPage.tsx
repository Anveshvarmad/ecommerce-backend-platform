import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { AuditLog, Paginated } from "../lib/types";

export function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [resourceType, setResourceType] = useState("");

  async function loadLogs() {
    const params = new URLSearchParams();
    if (resourceType) params.set("resource_type", resourceType);

    const response = await api.get<Paginated<AuditLog> | AuditLog[]>(
      `/audit/logs/?${params.toString()}`
    );

    const data = response.data;

    if (Array.isArray(data)) {
      setLogs(data);
    } else {
      setLogs(data.results);
    }
  }

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <main className="page">
      <h1 className="section-title">Audit Logs</h1>
      <p className="muted">Admin-only visibility into write operations and request IDs.</p>

      <div className="action-bar">
        <select
          className="input"
          value={resourceType}
          onChange={(event) => setResourceType(event.target.value)}
          style={{ maxWidth: 240 }}
        >
          <option value="">All resources</option>
          <option value="auth">Auth</option>
          <option value="product">Product</option>
          <option value="category">Category</option>
          <option value="cart">Cart</option>
          <option value="order">Order</option>
          <option value="payment">Payment</option>
          <option value="backoffice">Backoffice</option>
        </select>

        <button className="btn" onClick={loadLogs}>Filter</button>
      </div>

      <div className="glass-card table-card">
        <table className="table">
          <thead>
            <tr>
              <th>Action</th>
              <th>Actor</th>
              <th>Method</th>
              <th>Path</th>
              <th>Status</th>
              <th>Request ID</th>
              <th>Created</th>
            </tr>
          </thead>

          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{log.action}</td>
                <td>{log.actor_username || "anonymous"}</td>
                <td>{log.method}</td>
                <td>{log.path}</td>
                <td>{log.status_code}</td>
                <td>{log.correlation_id}</td>
                <td>{new Date(log.created_at).toLocaleString()}</td>
              </tr>
            ))}

            {logs.length === 0 && (
              <tr>
                <td colSpan={7}>No audit logs found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
