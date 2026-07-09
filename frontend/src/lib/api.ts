import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as any;

    if (typeof data === "string") return data;
    if (data?.detail) return data.detail;
    if (data?.non_field_errors?.length) return data.non_field_errors[0];

    const firstKey = data && typeof data === "object" ? Object.keys(data)[0] : null;
    if (firstKey && Array.isArray(data[firstKey])) return data[firstKey][0];
  }

  return "Something went wrong.";
}
