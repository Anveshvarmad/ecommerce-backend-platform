import time

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from django.test.utils import CaptureQueriesContext

from products.models import Category, Product


class Command(BaseCommand):
    help = "Benchmark catalog query performance and demonstrate select_related/cache improvements."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--search", type=str, default="wireless")
        parser.add_argument("--explain", action="store_true")

    def time_case(self, label, fn):
        start = time.perf_counter()

        with CaptureQueriesContext(connection) as captured_queries:
            result_count = fn()

        elapsed_ms = (time.perf_counter() - start) * 1000

        self.stdout.write(
            f"{label}: {elapsed_ms:.2f} ms | queries={len(captured_queries)} | rows={result_count}"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        search = options["search"]

        self.stdout.write(self.style.WARNING("Catalog Benchmark"))
        self.stdout.write(f"Products: {Product.objects.count()}")
        self.stdout.write(f"Categories: {Category.objects.count()}")
        self.stdout.write(f"Limit: {limit}")
        self.stdout.write("")

        def naive_product_list():
            rows = []
            products = Product.objects.filter(is_active=True).order_by("-created_at")[:limit]

            for product in products:
                rows.append(
                    {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category.name,
                        "vendor": product.vendor.username,
                        "price": str(product.price),
                    }
                )

            return len(rows)

        def optimized_product_list():
            rows = []
            products = (
                Product.objects
                .select_related("category", "vendor")
                .filter(is_active=True)
                .order_by("-created_at")[:limit]
            )

            for product in products:
                rows.append(
                    {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category.name,
                        "vendor": product.vendor.username,
                        "price": str(product.price),
                    }
                )

            return len(rows)

        def optimized_search():
            rows = []
            products = (
                Product.objects
                .select_related("category", "vendor")
                .filter(
                    Q(name__icontains=search)
                    | Q(description__icontains=search)
                    | Q(sku__icontains=search)
                    | Q(category__name__icontains=search),
                    is_active=True,
                )
                .order_by("-created_at")[:limit]
            )

            for product in products:
                rows.append(
                    {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category.name,
                        "vendor": product.vendor.username,
                    }
                )

            return len(rows)

        def category_summary():
            rows = list(
                Category.objects
                .filter(is_active=True)
                .order_by("name")
                .values("id", "name", "slug")[:limit]
            )

            return len(rows)

        def cache_set_get():
            key = "benchmark:catalog:sample"
            payload = {
                "items": list(
                    Product.objects
                    .filter(is_active=True)
                    .order_by("-created_at")
                    .values("id", "name", "sku", "price")[:limit]
                )
            }

            cache.set(key, payload, timeout=300)
            cached_payload = cache.get(key)

            return len(cached_payload["items"]) if cached_payload else 0

        self.time_case("Naive product list without select_related", naive_product_list)
        self.time_case("Optimized product list with select_related", optimized_product_list)
        self.time_case(f"Optimized search for '{search}'", optimized_search)
        self.time_case("Category summary query", category_summary)
        self.time_case("Redis cache set/get sample", cache_set_get)

        if options["explain"]:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("PostgreSQL EXPLAIN for optimized product list:"))

            plan = (
                Product.objects
                .select_related("category", "vendor")
                .filter(is_active=True)
                .order_by("-created_at")[:limit]
                .explain()
            )

            self.stdout.write(plan)
