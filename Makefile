.PHONY: up down build logs ps migrate makemigrations superuser shell test coverage seed benchmark cachekeys prod-up prod-down prod-logs

up:
	docker compose up -d

down:
	docker compose down --remove-orphans

build:
	docker compose up --build -d

logs:
	docker compose logs -f web

ps:
	docker compose ps

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

test:
	docker compose exec web pytest

coverage:
	docker compose exec web pytest --cov=. --cov-report=term-missing

seed:
	docker compose exec web python manage.py seed_catalog --vendors 25 --customers 500 --categories 30 --products 5000

benchmark:
	docker compose exec web python manage.py benchmark_catalog --limit 100 --explain

cachekeys:
	docker compose exec redis redis-cli -n 1 KEYS "*catalog*"

prod-up:
	docker compose -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml down --remove-orphans

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f web
