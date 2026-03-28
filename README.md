# PIZDo — Markdown to PDF (Typst)

FastAPI-сервис конвертации Markdown в PDF через Typst с настраиваемыми стилевыми профилями. Профили хранятся в Postgres; стили элементов (списки, параграфы, заголовки и т.д.) задаются по профилю и подставляются в Typst при генерации.

## Стек

- FastAPI, SQLAlchemy (async), asyncpg
- Pandoc (Markdown → Typst), Typst (Typst → PDF)
- Docker: Postgres 16, приложение на порту 8000

## Запуск

```bash
docker-compose up --build
```

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### Импортные шрифты Typst

- Пользовательские шрифты кладите в директорию `fonts/` в корне проекта.
- Для Docker эта папка автоматически монтируется в контейнер как `/app/fonts`.
- При генерации PDF сервис проверяет, что шрифт из профиля доступен Typst:
  - если шрифт есть системно или в `fonts/` — используется он;
  - если шрифт не найден — API вернет ошибку с названием отсутствующего семейства.

## Проверка через Swagger UI

1. Открыть <http://localhost:8000/docs>.
2. **POST /profiles** — создать профиль (например, имя `GOST default`).
3. **POST /profiles/{id}/bullet_list** — задать стили маркированного списка (тело можно пустое или с полями).
4. **POST /profiles/{id}/generate-pdf** — загрузить Markdown-файл, получить PDF в ответе.
5. При необходимости использовать **PATCH /profiles/{id}/bullet_list** и снова вызвать генерацию PDF.

## API

Полное описание запросов и схем — в [документации API](docs/API.md).

- **Profiles**: `POST/GET/PATCH/DELETE /profiles`, `GET /profiles/{id}`.
- **Element styles** (на каждый тип свой путь):
  `POST/GET/PATCH/PUT /profiles/{profile_id}/bullet_list`, `document`, `figure`, `footnote`, `heading`, `numbered_list`, `par`, `quote`, `table`.
- **Генерация**: `POST /profiles/{profile_id}/generate-pdf` — в теле запроса файл (Markdown), в ответе PDF.

Без авторизации (MVP).

## CI

GitHub Actions: при push/PR в `main` — тесты + ruff (lint/format).
Подробнее и настройка branch protection: [docs/CI_AND_PROTECTION.md](docs/CI_AND_PROTECTION.md).

## Тесты

Поведенческие тесты (ввод X → выход Y) через публичный API.

**Требования:**
- Postgres должен быть запущен (через docker-compose или локально)
- Тестовая БД `pizdo_test` создаётся автоматически при первом запуске

**Запуск:**

```bash
# 1. Запустить Postgres (если не запущен)
docker-compose up -d db

# 2. Очистить тестовую БД (опционально, если есть старые данные)
PGPASSWORD=postgres psql -h localhost -U postgres -d pizdo_test -c "TRUNCATE profiles, title_pages, bullet_list_styles, document_styles, figure_styles, footnote_styles, heading_styles, heading_level_styles, equation_styles, numbered_list_styles, outline_styles, page_styles, par_styles, quote_styles, raw_styles, table_styles, terms_styles, text_override_styles CASCADE;"

# 3. Установить зависимости и запустить тесты (рекомендуется uv)
uv pip install -r requirements.txt
uv run pytest tests/

# Или через pip + venv
pip install -r requirements.txt
source .venv/bin/activate  # если используете venv
pytest tests/
```

Только быстрые тесты (без pandoc/typst):
```bash
uv run pytest tests/ -m "not integration"
```

С интеграционным тестом (реальные pandoc + typst):
```bash
uv run pytest tests/ -m integration
```

**Примечание:** Если Postgres недоступен, тесты будут пропущены с понятным сообщением об ошибке.

## Frontend

Vue3 + Vite + TypeScript редактор (Markdown → Typst → PDF):

```bash
cd frontend && npm install && npm run dev
```

Фронтенд: http://localhost:5173. Требуется запущенный бэкенд на порту 8000.
