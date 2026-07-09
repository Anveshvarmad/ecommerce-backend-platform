import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product


class Command(BaseCommand):
    help = "Seed fake vendors, customers, categories, and products for performance testing."

    def add_arguments(self, parser):
        parser.add_argument("--vendors", type=int, default=25)
        parser.add_argument("--customers", type=int, default=500)
        parser.add_argument("--categories", type=int, default=30)
        parser.add_argument("--products", type=int, default=5000)
        parser.add_argument("--batch-size", type=int, default=1000)

    def handle(self, *args, **options):
        User = get_user_model()

        vendor_count = options["vendors"]
        customer_count = options["customers"]
        category_count = options["categories"]
        product_count = options["products"]
        batch_size = options["batch_size"]

        self.stdout.write(self.style.WARNING("Seeding fake ecommerce data..."))

        vendors = []
        for i in range(1, vendor_count + 1):
            username = f"seed_vendor_{i}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": "VENDOR",
                    "first_name": "Seed",
                    "last_name": f"Vendor{i}",
                },
            )
            user.role = "VENDOR"
            user.email = f"{username}@example.com"
            user.set_password("Password123!")
            user.save()
            vendors.append(user)

        for i in range(1, customer_count + 1):
            username = f"seed_customer_{i}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": "CUSTOMER",
                    "first_name": "Seed",
                    "last_name": f"Customer{i}",
                },
            )
            user.role = "CUSTOMER"
            user.email = f"{username}@example.com"
            user.set_password("Password123!")
            user.save()

        base_categories = [
            "Electronics",
            "Clothing",
            "Home",
            "Kitchen",
            "Books",
            "Sports",
            "Beauty",
            "Toys",
            "Automotive",
            "Garden",
            "Office",
            "Health",
            "Footwear",
            "Accessories",
            "Gaming",
            "Furniture",
            "Grocery",
            "Pet Supplies",
            "Tools",
            "Outdoor",
        ]

        categories = []
        for i in range(category_count):
            name = base_categories[i] if i < len(base_categories) else f"Category {i + 1}"
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"Seed category for {name.lower()} products.",
                    "is_active": True,
                },
            )
            categories.append(category)

        adjectives = [
            "Premium",
            "Wireless",
            "Smart",
            "Eco",
            "Compact",
            "Advanced",
            "Classic",
            "Portable",
            "Ultra",
            "Pro",
            "Modern",
            "Durable",
            "Essential",
            "Performance",
            "Lightweight",
        ]

        nouns = [
            "Headphones",
            "Backpack",
            "Desk Lamp",
            "Running Shoes",
            "Water Bottle",
            "Keyboard",
            "Mouse",
            "Jacket",
            "Coffee Maker",
            "Phone Stand",
            "Monitor",
            "Speaker",
            "Notebook",
            "Gaming Chair",
            "Fitness Tracker",
        ]

        existing_skus = set(
            Product.objects.filter(sku__startswith="SEED-").values_list("sku", flat=True)
        )

        products_to_create = []

        for i in range(1, product_count + 1):
            sku = f"SEED-{i:06d}"

            if sku in existing_skus:
                continue

            adjective = random.choice(adjectives)
            noun = random.choice(nouns)
            name = f"{adjective} {noun} {i}"

            price = Decimal(random.randint(999, 99999)) / Decimal("100")
            stock = random.randint(0, 1000)

            product = Product(
                vendor=random.choice(vendors),
                category=random.choice(categories),
                name=name,
                slug=slugify(f"{name}-{sku.lower()}"),
                sku=sku,
                description=f"Fake product description for {name}. Built for catalog search and performance testing.",
                price=price,
                stock_quantity=stock,
                is_active=True,
                image_url=f"https://example.com/products/{sku.lower()}.jpg",
                metadata={
                    "seeded": True,
                    "brand": random.choice(["VoltMax", "SoundMax", "UrbanNest", "FitCore", "DailyPro"]),
                    "rating": round(random.uniform(3.5, 5.0), 1),
                },
            )

            products_to_create.append(product)

            if len(products_to_create) >= batch_size:
                Product.objects.bulk_create(products_to_create, batch_size=batch_size)
                self.stdout.write(f"Created {len(products_to_create)} products...")
                products_to_create = []

        if products_to_create:
            Product.objects.bulk_create(products_to_create, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS("Fake ecommerce data seeding complete."))
        self.stdout.write(f"Vendors: {User.objects.filter(role='VENDOR').count()}")
        self.stdout.write(f"Customers: {User.objects.filter(role='CUSTOMER').count()}")
        self.stdout.write(f"Categories: {Category.objects.count()}")
        self.stdout.write(f"Products: {Product.objects.count()}")
