import { Link, Outlet, useNavigate } from "react-router-dom";
import { ShoppingBag, ShoppingCart, UserCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <>
      <header className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="logo">
            <span className="logo-mark">
              <ShoppingBag size={20} />
            </span>
            CommercePilot
          </Link>

          <nav className="nav-links">
            <Link className="nav-link" to="/products">Products</Link>

            {user?.role === "CUSTOMER" && (
              <>
                <Link className="nav-link" to="/cart">Cart</Link>
                <Link className="nav-link" to="/orders">Orders</Link>
              </>
            )}

            {!user ? (
              <>
                <Link className="nav-link" to="/login">Login</Link>
                <Link className="btn small" to="/register">Register</Link>
              </>
            ) : (
              <>
                <span className="badge">
                  <UserCircle size={16} />
                  {user.username} · {user.role}
                </span>
                <button className="btn secondary small" onClick={handleLogout}>
                  Logout
                </button>
              </>
            )}

            {user?.role === "CUSTOMER" && (
              <Link className="btn small" to="/cart">
                <ShoppingCart size={15} /> Cart
              </Link>
            )}
          </nav>
        </div>
      </header>

      <Outlet />
    </>
  );
}
