import { useEffect, useMemo, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../lib/api";
import type { AdminSummary } from "../lib/types";

export function AdminDashboardPage() {
  const [summary, setSummary] = useState<AdminSummary | null>(null);

  async function loadSummary() {
    const response = await api.get<AdminSummary>("/backoffice/admin/summary/");
    setSummary(response.data);
  }

  useEffect(() => {
    loadSummary();
  }, []);

  const orderData = useMemo(() => {
    if (!summary) return [];
    return Object.entries(summary.orders.by_status).map(([name, value]) => ({
      name,
      value,
    }));
  }, [summary]);

  const paymentData = useMemo(() => {
    if (!summary) return [];
    return Object.entries(summary.payments.by_status).map(([name, value]) => ({
      name,
      value,
    }));
  }, [summary]);

  if (!summary) {
    return <main className="page">Loading admin dashboard...</main>;
  }

  return (
    <main className="page">
      <h1 className="section-title">Admin Dashboard</h1>
      <p className="muted">Platform-wide users, catalog, orders, payments, and revenue.</p>

      <section className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Total Users</h3>
          <strong>{summary.users.total}</strong>
          <span className="muted">{summary.users.customers} customers</span>
        </div>

        <div className="dashboard-card">
          <h3>Total Products</h3>
          <strong>{summary.catalog.products}</strong>
          <span className="muted">{summary.catalog.active_products} active</span>
        </div>

        <div className="dashboard-card">
          <h3>Total Orders</h3>
          <strong>{summary.orders.total}</strong>
          <span className="muted">All statuses</span>
        </div>

        <div className="dashboard-card">
          <h3>Gross Revenue</h3>
          <strong>${summary.orders.gross_revenue}</strong>
          <span className="muted">Paid/fulfilled orders</span>
        </div>
      </section>

      <section className="admin-layout">
        <div className="glass-card chart-card">
          <h2>Orders by Status</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={orderData}>
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card chart-card">
          <h2>Payments by Status</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={paymentData}>
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </main>
  );
}
