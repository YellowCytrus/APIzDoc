#!/bin/sh
# Поставить штамп 002 на БД (схема уже создана SQLAlchemy).
# После этого: docker-compose up --build
# Миграция 003 применится при старте.
set -e
cd "$(dirname "$0")/.."
docker-compose run --rm app alembic stamp 002
