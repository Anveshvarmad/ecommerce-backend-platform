import { useEffect, useState } from "react";
import { api, getErrorMessage } from "../lib/api";
import type { Product, VendorSummary } from "../lib/types";

export function VendorDashboardPage() {
  const [summary, setSummary] = useState<VendorSummary | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [message, setMessage] = useState("");

  async function loadData() {
    const [summaryResponse, productResponse] = await Promise.all([
      api.get<VendorSummary>("/backoffice/vendor/summary/"),
      api.get<Product[]>("/backoffice/vendor/products/"),
    ]);

    setSummary(summaryResponse.data);
    setProducts(productResponse.data);
  }

  useEffect(() => {
    loadData();
  }, []);

  async function updateInventory(productId: number, stockQuantity: number, isActive: boolean) {
    setMessage("");

    try {
      await api.patch(`/backoffice/vendor/products/${productId}/inventory/`, {
        stock_quantity: stockQuantity,
        is_active: isActive,
      });

      setMessage("Inventory updated successfully.");
      await loadData();
    } catch (err) {
      setMessage(getErrorMessage(err));
    }
  }

  if (!summary) {
    return <main className="page">Loading vendor dashboard...</main>;
  }

  return (
    <main className="page">
      <h1 className="section-title">Vendor Dashboard</h1>
      <p className="muted">Manage inventory and track vendor sales performance.</p>

      <section className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Total Products</h3>
          <strong>{summary.products.total}</strong>
          <span className="muted">{summary.products.active} active</span>
        </div>

        <div className="dashboard-card">
          <h3>Low Stock</h3>
          <strong>{summary.products.low_stock}</strong>
          <span className="muted">Needs attention</span>
        </div>

        <div className="dashboard-card">
          <h3>Units Sold</h3>
          <strong>{summary.sales.units_sold}</strong>
          <span className="muted">Paid order items</span>
        </div>

        <div className="dashboard-card">
          <h3>Revenue</h3>
          <strong>${summary.sales.revenue}</strong>
          <span className="muted">Vendor sales</span>
        </div>
      </section>

      {message && <div className="alert" style={{ marginBottom: 18 }}>{message}</div>}

      <div className="glass-card table-card">
        <h2>Inventory</h2>

        <table className="table">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Stock</th>
              <th>Status</th>
              <th>Save</th>
            </tr>
          </thead>

          <tbody>
            {products.map((product) => (
              <InventoryRow
                key={product.id}
                product={product}
                onSave={updateInventory}
              />
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}

function InventoryRow({
  product,
  onSave,
}: {
  product: Product;
  onSave: (productId: number, stockQuantity: number, isActive: boolean) => Promise<void>;
}) {
  const [stock, setStock] = useState(product.stock_quantity);
  const [isActive, setIsActive] = useState(product.is_active);

  return (
    <tr>
      <td>
        <strong>{product.name}</strong>
        <div className="muted">${product.price}</div>
      </td>
      <td>{product.sku}</td>
      <td>
        <input
          className="input"
          type="number"
          min={0}
          style={{ width: 110 }}
          value={stock}
          onChange={(event) => setStock(Number(event.target.value))}
        />
      </td>
      <td>
        <select
          className="input"
          value={isActive ? "active" : "inactive"}
          onChange={(event) => setIsActive(event.target.value === "active")}
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </td>
      <td>
        <button className="btn small" onClick={() => onSave(product.id, stock, isActive)}>
          Save
        </button>
      </td>
    </tr>
  );
}
