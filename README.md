# E-Commerce Backend Platform

A production-style full-stack e-commerce platform built with Django, PostgreSQL, Redis, Celery, Docker, and React.

This project simulates a real e-commerce backend system with customer shopping flows, vendor inventory management, support order operations, admin analytics, Redis caching, fake payments, audit logs, background jobs, and automated tests.

---

## Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT Authentication
- Pytest
- Docker
- Gunicorn

### Frontend
- React
- TypeScript
- Vite
- Axios
- React Router
- Framer Motion
- Recharts

---

## Features

### Customer
- Register and login
- Browse products
- Search and filter catalog
- Add products to cart
- Update cart quantity
- Checkout
- View orders
- Simulate fake payment

### Vendor
- View vendor dashboard
- Track sales summary
- Manage product inventory
- Activate or deactivate products

### Support
- Search customer orders
- View order status
- Update order lifecycle status

### Admin
- View platform metrics
- Track users, products, orders, payments, and revenue
- View audit logs
- Monitor write operations

---

## Architecture

```mermaid
flowchart TD
    A[React Frontend] --> B[Django REST API]

    B --> C[Auth and RBAC]
    B --> D[Product Catalog]
    B --> E[Cart Service]
    B --> F[Order Service]
    B --> G[Payment Service]
    B --> H[Backoffice APIs]
    B --> I[Audit Logging]

    C --> J[(PostgreSQL)]
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J

    D --> K[(Redis Cache)]
    B --> K

    F --> L[Celery Worker]
    G --> L
    L --> M[Async Emails and Receipts]

    N[Celery Beat] --> O[Abandoned Cart Cleanup]
    N --> K
