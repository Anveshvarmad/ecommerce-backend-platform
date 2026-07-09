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
