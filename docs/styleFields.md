`frontend/src/config/styleFields.ts` отвечает за **описание структуры UI-редактора стилей** на фронтенде: какие вкладки бывают, какие поля у каждого элемента профиля можно менять и с какими типами/опциями.

Ключевые экспорты в этом файле:

- `STYLE_TAB_TREE`: дерево вкладок/секций (например `page`, `document`, `heading_1..heading_6`, списки, `table`, `figure`, `terms`, `outline` и т.п.) и для каждой секции набор `fields`.
- `FieldDef`: описание одного поля (тип `number/boolean/string/select/markers`, min/max/step, варианты `options`, подсказки и т.д.).
- `TEXT_OVERRIDE_FIELDS`: список полей, которые показывает UI, когда включен переключатель “`Задать свой стиль для текста`”.
- `TITLE_TEXT_DEFAULTS`: дефолтные значения для текстовых стилей на титульной странице.
- `VARIABLE_ALIGN_OPTIONS`: варианты выравнивания для переменных.
- `collectElementKeys(STYLE_TAB_TREE)`: собирает все `elementKey` из дерева вкладок (нужен для “bulk-loading” всех стилей).

Где это используется:
- `frontend/src/views/Styles.vue` подставляет `STYLE_TAB_TREE` в `NestedTabs`, то есть это именно конфиг для интерфейса.
- `frontend/src/composables/useStyleEditor.ts` использует `collectElementKeys(STYLE_TAB_TREE)`, чтобы загрузить/патчить стили пачкой по ключам.
- `frontend/src/components/styles/StyleForm.vue` использует `TEXT_OVERRIDE_FIELDS`, чтобы отрисовать поля “текст-оверрайда”.
