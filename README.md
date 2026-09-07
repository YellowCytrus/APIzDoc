# FluentDocs — Пиши содержание, оформление система сделает сама

FluentDocs — это приложение для написания книг, отчётов и любых документов в отрыве от их оформления. Ты один раз настраиваешь стили под нужный стандарт, а дальше пишешь практически чистым Markdown — системой, которая по своей сути довольно прост в написании. Хоть Markdown и простой, FluentDocs даёт множество возможностей, ускоряющих работу с ним.

## Философия

> Проект создан для обычного пользователя — не технаря. Идея проста: **один раз настроить стили** для своих документов, а затем писать книги, отчёты, любые документы в отрыве от их оформления, практически чистым Markdown.

> Цель FluentDocs — сделать простое и понятное приложение, которое избавит людей от потери времени на правку оформления, которое в привычных офисных программах нередко «плывёт».

> С самого начала проект разрабатывается для работы именно с университетским стандартом СФУ. Поэтому мы выдвигаем такой тезис: **если у университета есть стандарт оформления, то пусть студенты и сотрудники не тратят своё ценное время на пресловутые правки отступов, а занимаются исключительно содержательной частью своих документов — вся остальная рутина достанется системе.**

## Демо

![Демонстрация FluentDocs](table_demo.gif)

Также доступно [короткое видеодемо](https://drive.google.com/file/d/1TU5eeBewRLgxIL2qAtel6y9PMwQgP9Ad/view?usp=sharing).

## Что в планах

1. Доработать и отладить базовые настройки стилей и фичи.
2. Продумать UX/UI, который позволит любому человеку быстро вникнуть в тонкости настройки стилей.
3. **Бонусом:** добавить AI-функции — у нас уже есть опыт в построении агентных систем. Можно сделать простой чат, в который пользователь сможет скинуть все свои скриншоты, заметки и сопутствующие документы, а на выходе получить, например, готовый отчёт.

---

# Техническая часть

## Обзор

FluentDocs — FastAPI-сервис конвертации Markdown в PDF через Typst с настраиваемыми стилевыми профилями. Профили хранятся в Postgres; стили элементов (списки, параграфы, заголовки и т.д.) задаются по профилю и подставляются в Typst при генерации.

Рекомендуем сначала ознакомиться с [документацией языка Typst](https://typst.app/docs/).

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
  - если шрифт не найден — API вернёт ошибку с названием отсутствующего семейства.

## Проверка через Swagger UI

1. Открыть <http://localhost:8000/docs>.
2. **POST /profiles** — создать профиль (например, имя `GOST default`).
3. **POST /profiles/{id}/bullet_list** — задать стили маркированного списка (тело можно пустое или с полями).
4. **POST /profiles/{id}/generate-pdf** — загрузить Markdown-файл, получить PDF в ответе.
5. При необходимости использовать **PATCH /profiles/{id}/bullet_list** и снова вызвать генерацию PDF.

## Документация

- **WIKI (архитектура, потоки, Typst, фронт):** [docs/wiki/SUMMARY.md](docs/wiki/SUMMARY.md)
- **REST API (кратко + ссылки):** [docs/API.md](docs/API.md) — детальная шпаргалка в [docs/wiki/Backend/API.md](docs/wiki/Backend/API.md); на запущенном сервере — [Swagger](http://localhost:8000/docs)

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
