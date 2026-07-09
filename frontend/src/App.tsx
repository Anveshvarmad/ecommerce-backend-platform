import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ProductsPage } from "./pages/ProductsPage";
import { CartPage } from "./pages/CartPage";
import { CheckoutPage } from "./pages/CheckoutPage";
import { OrdersPage } from "./pages/OrdersPage";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { VendorDashboardPage } from "./pages/VendorDashboardPage";
import { SupportDashboardPage } from "./pages/SupportDashboardPage";
import { AuditLogsPage } from "./pages/AuditLogsPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route
              path="/cart"
              element={
                <ProtectedRoute roles={["CUSTOMER"]}>
                  <CartPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/checkout"
              element={
                <ProtectedRoute roles={["CUSTOMER"]}>
                  <CheckoutPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/orders"
              element={
                <ProtectedRoute roles={["CUSTOMER"]}>
                  <OrdersPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/vendor"
              element={
                <ProtectedRoute roles={["VENDOR"]}>
                  <VendorDashboardPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/support"
              element={
                <ProtectedRoute roles={["SUPPORT"]}>
                  <SupportDashboardPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin"
              element={
                <ProtectedRoute roles={["ADMIN"]}>
                  <AdminDashboardPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/audit"
              element={
                <ProtectedRoute roles={["ADMIN"]}>
                  <AuditLogsPage />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
