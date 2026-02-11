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
