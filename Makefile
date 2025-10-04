# Convenience Makefile for running and operating the stack
# Override HOST like: make health HOST=192.168.10.121:8000
HOST ?= localhost:8000

.PHONY: up down logs restart rebuild health events recent feed latest post reload metrics creds

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

rebuild:
	docker compose down
	docker compose up -d --build

health:
	curl -fsS http://$(HOST)/healthz || true

events:
	curl -N http://$(HOST)/events || true

recent:
	curl -fsS http://$(HOST)/api/recent | jq || curl -fsS http://$(HOST)/api/recent || true

feed:
	curl -fsS http://$(HOST)/api/feed | jq || curl -fsS http://$(HOST)/api/feed || true

latest:
	curl -fsS http://$(HOST)/api/latest | jq || curl -fsS http://$(HOST)/api/latest || true

post:
	curl -fsS -X POST http://$(HOST)/api/post-now || true

reload:
	curl -fsS -X POST http://$(HOST)/api/reload-schedule || true

metrics:
	curl -fsS http://$(HOST)/api/metrics | jq || curl -fsS http://$(HOST)/api/metrics || true

creds:
	curl -fsS http://$(HOST)/api/credentials | jq || curl -fsS http://$(HOST)/api/credentials || true