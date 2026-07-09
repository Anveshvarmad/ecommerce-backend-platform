import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Activity, Database, ShieldCheck, ShoppingCart } from "lucide-react";

export function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
        >
          <span className="badge">
            <Activity size={16} />
            Production-style e-commerce backend + frontend
          </span>

          <h1>
            Scalable commerce platform with{" "}
            <span className="gradient-text">real backend flows.</span>
          </h1>

          <p>
            Browse products, manage cart, checkout orders, simulate payments,
            and test RBAC-backed workflows powered by Django, PostgreSQL,
            Redis, Celery, Docker, and React.
          </p>

          <div className="hero-actions">
            <Link className="btn" to="/products">Explore Products</Link>
            <Link className="btn secondary" to="/register">Create Account</Link>
          </div>
        </motion.div>

        <motion.div
          className="glass-card dashboard-preview"
          initial={{ opacity: 0, scale: 0.96, y: 24 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.1 }}
        >
          <div className="metric-grid">
            <div className="metric">
              <ShoppingCart />
              <div className="metric-value">5K+</div>
              <div className="metric-label">Simulated daily transactions</div>
            </div>

            <div className="metric">
              <Database />
              <div className="metric-value">Redis</div>
              <div className="metric-label">Cached catalog reads</div>
            </div>

            <div className="metric">
              <ShieldCheck />
              <div className="metric-value">RBAC</div>
              <div className="metric-label">Customer, vendor, support, admin</div>
            </div>

            <div className="metric">
              <Activity />
              <div className="metric-value">Celery</div>
              <div className="metric-label">Async order/payment jobs</div>
            </div>
          </div>
        </motion.div>
      </section>
    </main>
  );
}
