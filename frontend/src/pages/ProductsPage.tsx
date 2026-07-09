import { useEffect, useMemo, useState } from "react";
import { Package, Search } from "lucide-react";
import { motion } from "framer-motion";
import { api, getErrorMessage } from "../lib/api";
import type { Paginated, Product } from "../lib/types";
import { useAuth } from "../context/AuthContext";

export function ProductsPage() {
  const { user } = useAuth();

  const [products, setProducts] = useState<Product[]>([]);
  const [q, setQ] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [inStock, setInStock] = useState("true");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  const query = useMemo(() => {
    const params = new URLSearchParams();
    params.set("page_size", "50");

    if (q) params.set("q", q);
    if (minPrice) params.set("min_price", minPrice);
    if (maxPrice) params.set("max_price", maxPrice);
    if (inStock === "true") params.set("in_stock", "true");

    return params.toString();
  }, [q, minPrice, maxPrice, inStock]);

  async function loadProducts() {
    setLoading(true);

    try {
      const response = await api.get<Paginated<Product>>(`/catalog/products/?${query}`);
      setProducts(response.data.results);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, [query]);

  async function addToCart(productId: number) {
    setMessage("");

    if (!user) {
      setMessage("Please login as a customer to add products to cart.");
      return;
    }

    if (user.role !== "CUSTOMER") {
      setMessage("Only customers can add products to cart.");
      return;
    }

    try {
      await api.post("/cart/items/", {
        product_id: productId,
        quantity: 1,
      });

      setMessage("Product added to cart.");
    } catch (err) {
      setMessage(getErrorMessage(err));
    }
  }

  return (
    <main className="page">
      <div className="row">
        <div>
          <h1 className="section-title">Product Catalog</h1>
          <p className="muted">Search cached product APIs powered by Django + Redis.</p>
        </div>
      </div>

      <div className="toolbar">
        <div style={{ position: "relative" }}>
          <Search
            size={18}
            style={{ position: "absolute", left: 14, top: 15, color: "#94a3b8" }}
          />
          <input
            className="input"
            style={{ paddingLeft: 42 }}
            placeholder="Search headphones, charger, shoes..."
            value={q}
            onChange={(event) => setQ(event.target.value)}
          />
        </div>

        <input
          className="input"
          placeholder="Min price"
          value={minPrice}
          onChange={(event) => setMinPrice(event.target.value)}
        />

        <input
          className="input"
          placeholder="Max price"
          value={maxPrice}
          onChange={(event) => setMaxPrice(event.target.value)}
        />

        <select
          className="input"
          value={inStock}
          onChange={(event) => setInStock(event.target.value)}
        >
          <option value="true">In stock</option>
          <option value="all">All products</option>
        </select>
      </div>

      {message && <div className="alert" style={{ marginBottom: 18 }}>{message}</div>}

      {loading ? (
        <div className="glass-card table-card">Loading products...</div>
      ) : (
        <div className="grid">
          {products.map((product, index) => (
            <motion.article
              key={product.id}
              className="glass-card product-card"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.025 }}
            >
              <div className="product-img">
                <Package size={46} />
              </div>

              <h3>{product.name}</h3>
              <p className="muted">{product.category_name} · {product.sku}</p>

              <div className="row" style={{ marginTop: 16 }}>
                <div>
                  <div className="price">${product.price}</div>
                  <div className="stock">{product.stock_quantity} in stock</div>
                </div>

                <button className="btn small" onClick={() => addToCart(product.id)}>
                  Add
                </button>
              </div>
            </motion.article>
          ))}
        </div>
      )}
    </main>
  );
}
