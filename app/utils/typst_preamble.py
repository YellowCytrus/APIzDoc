"""
Построение преамбулы Typst #set из элементов профиля.
Typst использует строки в двойных кавычках; экранируем " и \\ внутри.
"""
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement


def _typst_str(s: str) -> str:
    """Форматирует строку Python как литерал строки Typst (в двойных кавычках)."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _typst_list_spacing(s: str) -> str:
    """Интервал списка/enum в Typst: 'auto' — ключевое слово, 'tight'/'loose' преобразуются в размеры."""
    if s == "auto":
        return "auto"
    if s == "tight":
        return "0.5em"
    if s == "loose":
        return "1em"
    return "auto"


def _bullet_list_line(e: ProfileElement) -> str:
    markers = [e.marker1, e.marker2, e.marker3]
    markers_str = ", ".join(_typst_str(m) for m in markers)
    return (
        f"#set list(tight: {str(e.tight).lower()}, "
        f"indent: {e.indent_pt}pt, body-indent: {e.body_indent_em}em, "
        f"spacing: {_typst_list_spacing(e.spacing)}, marker: ({markers_str}))"
    )


def _document_line(e: ProfileElement) -> str:
    return (
        f"#set text(size: {e.font_size_pt}pt)"
        f"\n#set par(leading: {e.line_spacing_em}em)"
    )


def _figure_line(e: ProfileElement) -> str:
    w = f"{e.figure_width_em}em" if e.figure_width_em else "auto"
    h = f"{e.figure_height_em}em" if e.figure_height_em else "auto"
    return f"#set image(width: {w}, height: {h})"


def _footnote_line(e: ProfileElement) -> str:
    return f"#set footnote(numbering: {_typst_str(e.footnote_marker_fmt)})"


def _heading_line(e: ProfileElement) -> str:
    num = e.heading_numbering if e.heading_numbering != "none" else "none"
    return f"#set heading(numbering: {_typst_str(num)})"


def _numbered_list_line(e: ProfileElement) -> str:
    return (
        f"#set enum(tight: {str(e.tight).lower()}, "
        f"indent: {e.indent_pt}pt, body-indent: {e.body_indent_em}em, "
        f"spacing: {_typst_list_spacing(e.spacing)})"
    )


def _par_line(e: ProfileElement) -> str:
    return f"#set par(spacing: {e.spacing_em}em)"


def _quote_line(e: ProfileElement) -> str:
    return (
        f"#set quote(block: true)\n"
        f"#show quote: set pad(x: {e.quote_indent_em}em)"
    )


def _table_line(e: ProfileElement) -> str:
    return f"#set table(stroke: {e.table_stroke})"


_BUILDERS = {
    ElementType.bullet_list: _bullet_list_line,
    ElementType.document: _document_line,
    ElementType.figure: _figure_line,
    ElementType.footnote: _footnote_line,
    ElementType.heading: _heading_line,
    ElementType.numbered_list: _numbered_list_line,
    ElementType.par: _par_line,
    ElementType.quote: _quote_line,
    ElementType.table: _table_line,
}


def build_typst_preamble(elements: list[ProfileElement]) -> str:
    """Строит преамбулу Typst #set из элементов профиля. Один блок на элемент."""
    lines: list[str] = []
    for e in elements:
        fn = _BUILDERS.get(e.element_type)
        if fn is None:
            continue
        part = fn(e)
        lines.extend(part.split("\n"))
    return "\n".join(lines) + "\n" if lines else ""
