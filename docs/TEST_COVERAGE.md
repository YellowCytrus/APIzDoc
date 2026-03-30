# Покрытие тестов (регрессия)

| Модуль | Эндпоинт/область | Что проверяет |
|--------|------------------|---------------|
| **test_profiles_api** | `POST /profiles` | Создание, 200, тело с name, id |
| | `GET /profiles` | Список, созданные профили в списке |
| | `GET /profiles?limit=&offset=` | Пагинация (limit ≤ 2) |
| | `GET /profiles/{id}` | 200, тело |
| | `GET /profiles/99999` | 404 |
| | `PATCH /profiles/{id}` | Обновление name |
| | `PATCH /profiles/99999` | 404 |
| | `DELETE /profiles/{id}` | 204, затем 404 при GET |
| | `DELETE /profiles/99999` | 404 |
| **test_element_styles_api** | `POST /profiles/{id}/bullet_list` | Создание стилей, tight, marker, spacing |
| | `GET /profiles/{id}/bullet_list` | Получение стилей |
| | `GET /profiles/{id}/bullet_list` (без POST) | Auto-create defaults (tight, marker) |
| | `PATCH /profiles/{id}/bullet_list` | 404 если стили не заданы |
| | `PATCH /profiles/{id}/bullet_list` | 200 после POST |
| | `GET/POST/PATCH /profiles/99999/bullet_list` | 404 для несуществующего профиля |
| **test_title_pages_api** | `POST /title-pages` | Создание, name, id, content |
| | `GET /title-pages` | Список, созданные в списке |
| | `GET /title-pages/{id}` | 200, тело |
| | `GET /title-pages/99999` | 404 |
| | `PATCH /title-pages/{id}` | Обновление name |
| | `DELETE /title-pages/{id}` | 204, затем 404 |
| | `DELETE /title-pages/99999` | 404 |
| **test_preamble_api** | `GET /profiles/{id}/preamble` | 200, text/plain, non-empty body |
| | `GET /profiles/99999/preamble` | 404 |
| **test_generate_pdf_api** | `POST /profiles/{id}/generate-pdf` | 200, application/pdf, PDF header |
| | | Content-Disposition с именем файла |
| | `POST /profiles/99999/generate-pdf` | 404 |
| | Пустой файл | 400 |
| | Файл > 10 MB | 413 |
| | Расширение не .md | 400 |
| | Ошибка pandoc | 500 |
| | Ошибка typst | 500 |
| **test_generate_pdf_integration** | Full cycle | Реальные pandoc + typst, md → PDF (skip без бинарников) |

## Не покрыто

- Элементы стилей: только `bullet_list`; `document`, `par`, `heading`, `figure`, `equation` и др. — нет
- Эндпоинты `heading/{level}`, `equation` и т.п.
- Preamble: содержимое не валидируется, только 200 и тип
- Title pages: `content` не полностью проверяется
