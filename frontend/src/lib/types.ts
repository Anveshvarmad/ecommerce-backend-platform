export type Role = "CUSTOMER" | "VENDOR" | "SUPPORT" | "ADMIN";

export type User = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
};

export type Product = {
  id: number;
  vendor: number;
  vendor_username: string;
  category: number;
  category_name: string;
  name: string;
  slug: string;
  sku: string;
  description: string;
  price: string;
  stock_quantity: number;
  is_active: boolean;
  image_url: string;
  metadata: Record<string, unknown>;
  updated_at?: string;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type CartItem = {
  id: number;
  product: Product;
  quantity: number;
  line_total: string;
};

export type Cart = {
  id: number;
  status: string;
  items: CartItem[];
  total_items: number;
  subtotal: string;
};

export type Order = {
  id: number;
  order_number: string;
  user?: number;
  user_username?: string;
  status: string;
  subtotal_amount: string;
  tax_amount: string;
  shipping_fee: string;
  total_amount: string;
  total_items: number;
  created_at: string;
};

export type Payment = {
  id: number;
  payment_number: string;
  status: string;
  amount: string;
  currency: string;
  order_number: string;
};

export type AdminSummary = {
  users: {
    total: number;
    customers: number;
    vendors: number;
    support: number;
    admins: number;
  };
  catalog: {
    products: number;
    active_products: number;
    low_stock_products: number;
  };
  orders: {
    total: number;
    by_status: Record<string, number>;
    gross_revenue: string;
  };
  payments: {
    total: number;
    by_status: Record<string, number>;
  };
  generated_at: string;
};

export type VendorSummary = {
  vendor: {
    id: number;
    username: string;
    email: string;
  };
  products: {
    total: number;
    active: number;
    low_stock: number;
  };
  sales: {
    sold_line_items: number;
    paid_line_items: number;
    units_sold: number;
    revenue: string;
  };
  generated_at: string;
};

export type AuditLog = {
  id: number;
  actor: number | null;
  actor_username: string | null;
  action: string;
  method: string;
  path: string;
  status_code: number;
  resource_type: string;
  resource_id: string;
  ip_address: string | null;
  correlation_id: string;
  created_at: string;
};
