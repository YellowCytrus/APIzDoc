"""
Построение преамбулы Typst #set из стилей профиля.
Typst использует строки в двойных кавычках; экранируем " и \\ внутри.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.sqlalchemy.profile import Profile
    from app.models.sqlalchemy.styles import (
        BulletListStyle,
        DocumentStyle,
        EquationStyle,
        FigureStyle,
        FootnoteStyle,
        HeadingLevelStyle,
        HeadingStyle,
        NumberedListStyle,
        OutlineStyle,
        PageStyle,
        ParStyle,
        QuoteStyle,
        RawStyle,
        TableStyle,
        TermsStyle,
    )


def _typst_str(s: str) -> str:
    """Форматирует строку Python как литерал строки Typst (в двойных кавычках)."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


# Шрифты, отсутствующие в Typst → встроенные аналоги
_FONT_ALIASES: dict[str, str] = {
    "times new roman": "Libertinus Serif",
    "times": "Libertinus Serif",
    "arial": "DejaVu Sans",
    "helvetica": "DejaVu Sans",
    "courier new": "DejaVu Sans Mono",
    "courier": "DejaVu Sans Mono",
}


def _typst_font(font: str) -> str:
    """Нормализует имя шрифта для Typst (алиасы для отсутствующих, пустой → дефолт)."""
    s = (font or "").strip()
    if not s:
        return "libertinus serif"
    key = s.lower()
    return _FONT_ALIASES.get(key, font)


def _typst_list_spacing(s: str) -> str:
    """Интервал списка/enum в Typst: 'auto' — ключевое слово, 'tight'/'loose' преобразуются в размеры."""
    if s == "auto":
        return "auto"
    if s == "tight":
        return "0.5em"
    if s == "loose":
        return "1em"
    return "auto"


def _typst_bool(val: bool | None) -> str:
    """bool → Typst true/false/auto."""
    if val is None:
        return "auto"
    return str(val).lower()


def _text_override_to_typst_args(to: Any) -> list[str]:
    """Build #set text(...) args from TextOverrideStyle."""
    args: list[str] = [f"size: {to.font_size}pt"]
    font = _typst_font(to.font)
    if font != "libertinus serif":
        args.append(f"font: {_typst_str(font)}")
    if to.weight != "regular":
        args.append(f"weight: {_typst_str(to.weight)}")
    if to.style != "normal":
        args.append(f"style: {_typst_str(to.style)}")
    if to.fill != "black":
        args.append(f"fill: {to.fill}")
    if to.lang != "en":
        args.append(f"lang: {_typst_str(to.lang)}")
    if to.region is not None:
        args.append(f"region: {_typst_str(to.region)}")
    if to.tracking != 0.0:
        args.append(f"tracking: {to.tracking}pt")
    if to.word_spacing != 100.0:
        args.append(f"spacing: {to.word_spacing}%")
    if to.hyphenate is not None:
        args.append(f"hyphenate: {_typst_bool(to.hyphenate)}")
    if not to.ligatures:
        args.append("ligatures: false")
    if to.number_type != "auto":
        args.append(f"number-type: {_typst_str(to.number_type)}")
    if to.number_width != "auto":
        args.append(f"number-width: {_typst_str(to.number_width)}")
    return args


def _show_set_text_for_element(selector: str, style_with_override: Any) -> str:
    """Return #show <selector>: set text(...) when style has text_override_style, else ''."""
    if style_with_override is None:
        return ""
    to = getattr(style_with_override, "text_override_style", None)
    if to is None:
        return ""
    text_args = _text_override_to_typst_args(to)
    return f"#show {selector}: set text({', '.join(text_args)})"


# ---------------------------------------------------------------------------
# Element builders
# ---------------------------------------------------------------------------


def _bullet_list_line(e: BulletListStyle) -> str:
    markers_str = ", ".join(_typst_str(m) for m in e.marker)
    return (
        f"#set list(tight: {str(e.tight).lower()}, "
        f"indent: {e.indent}pt, body-indent: {e.body_indent}em, "
        f"spacing: {_typst_list_spacing(e.spacing)}, marker: ({markers_str}))"
    )


def _document_line(e: DocumentStyle) -> str:
    parts: list[str] = []
    text_args: list[str] = [f"size: {e.font_size}pt"]
    font = _typst_font(e.font)
    if font != "libertinus serif":
        text_args.append(f"font: {_typst_str(font)}")
    if e.weight != "regular":
        text_args.append(f"weight: {_typst_str(e.weight)}")
    if e.style != "normal":
        text_args.append(f"style: {_typst_str(e.style)}")
    if e.fill != "black":
        text_args.append(f"fill: {e.fill}")
    if e.lang != "en":
        text_args.append(f"lang: {_typst_str(e.lang)}")
    if e.region is not None:
        text_args.append(f"region: {_typst_str(e.region)}")
    if e.tracking != 0.0:
        text_args.append(f"tracking: {e.tracking}pt")
    if e.word_spacing != 100.0:
        text_args.append(f"spacing: {e.word_spacing}%")
    if e.hyphenate is not None:
        text_args.append(f"hyphenate: {_typst_bool(e.hyphenate)}")
    if not e.ligatures:
        text_args.append("ligatures: false")
    if e.number_type != "auto":
        text_args.append(f"number-type: {_typst_str(e.number_type)}")
    if e.number_width != "auto":
        text_args.append(f"number-width: {_typst_str(e.number_width)}")
    parts.append(f"#set text({', '.join(text_args)})")
    par_args: list[str] = [f"leading: {e.line_spacing}em"]
    if e.justify:
        par_args.append("justify: true")
    parts.append(f"#set par({', '.join(par_args)})")
    return "\n".join(parts)


def _figure_line(e: FigureStyle) -> str:
    parts: list[str] = []
    img_args: list[str] = []
    w = f"{e.width}em" if e.width else "auto"
    h = f"{e.height}em" if e.height else "auto"
    img_args.append(f"width: {w}")
    img_args.append(f"height: {h}")
    if e.fit != "cover":
        img_args.append(f"fit: {_typst_str(e.fit)}")
    parts.append(f"#set image({', '.join(img_args)})")
    fig_args: list[str] = []
    if e.placement != "none":
        fig_args.append(f"placement: {e.placement}")
    if e.gap != 0.65:
        fig_args.append(f"gap: {e.gap}em")
    if not e.outlined:
        fig_args.append("outlined: false")
    if fig_args:
        parts.append(f"#set figure({', '.join(fig_args)})")
    return "\n".join(parts)


def _footnote_line(e: FootnoteStyle) -> str:
    parts: list[str] = [
        f"#set footnote(numbering: {_typst_str(e.marker_format)})",
    ]
    entry_args: list[str] = []
    if e.clearance != 1.0:
        entry_args.append(f"clearance: {e.clearance}em")
    if e.gap != 0.5:
        entry_args.append(f"gap: {e.gap}em")
    if e.indent != 1.0:
        entry_args.append(f"indent: {e.indent}em")
    if entry_args:
        parts.append(f"#set footnote.entry({', '.join(entry_args)})")
    return "\n".join(parts)


def _heading_line(e: HeadingStyle) -> str:
    """Only numbering (global for all levels)."""
    num = e.numbering if e.numbering != "none" else "none"
    if num == "none":
        return "#set heading(numbering: none)"
    return f"#set heading(numbering: {_typst_str(num)})"


def _numbered_list_line(e: NumberedListStyle) -> str:
    args: list[str] = [
        f"tight: {str(e.tight).lower()}",
        f"indent: {e.indent}pt",
        f"body-indent: {e.body_indent}em",
        f"spacing: {_typst_list_spacing(e.spacing)}",
    ]
    if e.numbering != "1.":
        args.append(f"numbering: {_typst_str(e.numbering)}")
    if e.start is not None:
        args.append(f"start: {e.start}")
    if e.full:
        args.append("full: true")
    if e.reversed:
        args.append("reversed: true")
    if e.number_align != "end+top":
        args.append(f"number-align: {e.number_align}")
    return f"#set enum({', '.join(args)})"


def _par_line(e: ParStyle) -> str:
    args: list[str] = [f"spacing: {e.spacing}em"]
    if e.first_line_indent != 0.0:
        args.append(f"first-line-indent: (amount: {e.first_line_indent}em, all: true)")
    if e.hanging_indent != 0.0:
        args.append(f"hanging-indent: {e.hanging_indent}em")
    if e.linebreaks != "auto":
        args.append(f"linebreaks: {_typst_str(e.linebreaks)}")
    return f"#set par({', '.join(args)})"


def _quote_line(e: QuoteStyle) -> str:
    parts: list[str] = []
    q_args: list[str] = [f"block: {str(e.block).lower()}"]
    if e.quotes != "auto":
        q_args.append(f"quotes: {e.quotes}")
    parts.append(f"#set quote({', '.join(q_args)})")
    parts.append(f"#show quote: set pad(x: {e.indent}em)")
    return "\n".join(parts)


def _table_line(e: TableStyle) -> str:
    args: list[str] = [f"stroke: {e.stroke}"]
    if e.align != "auto":
        args.append(f"align: {e.align}")
    if e.inset != "5pt":
        args.append(f"inset: {e.inset}")
    if e.fill != "none":
        args.append(f"fill: {e.fill}")
    return f"#set table({', '.join(args)})"


# ---------------------------------------------------------------------------
# New element builders
# ---------------------------------------------------------------------------


def _page_line(e: PageStyle) -> str:
    args: list[str] = [f"{_typst_str(e.paper)}"]
    if e.flipped:
        args.append("flipped: true")
    margin_parts: list[str] = []
    if e.margin_top != 2.5:
        margin_parts.append(f"top: {e.margin_top}cm")
    if e.margin_bottom != 2.5:
        margin_parts.append(f"bottom: {e.margin_bottom}cm")
    if e.margin_left != 2.5:
        margin_parts.append(f"left: {e.margin_left}cm")
    if e.margin_right != 2.5:
        margin_parts.append(f"right: {e.margin_right}cm")
    if margin_parts:
        args.append(f"margin: ({', '.join(margin_parts)})")
    if e.columns != 1:
        args.append(f"columns: {e.columns}")
    if e.numbering != "none":
        args.append(f"numbering: {_typst_str(e.numbering)}")
    if e.number_align != "center+bottom":
        args.append(f"number-align: {e.number_align}")
    return f"#set page({', '.join(args)})"


def _raw_line(e: RawStyle) -> str:
    args: list[str] = []
    if e.tab_size != 2:
        args.append(f"tab-size: {e.tab_size}")
    if e.align != "start":
        args.append(f"align: {e.align}")
    if e.theme == "none":
        args.append("theme: none")
    if not args:
        return ""
    return f"#set raw({', '.join(args)})"


def _terms_line(e: TermsStyle) -> str:
    args: list[str] = [
        f"tight: {str(e.tight).lower()}",
    ]
    if e.indent != 0.0:
        args.append(f"indent: {e.indent}pt")
    if e.hanging_indent != 2.0:
        args.append(f"hanging-indent: {e.hanging_indent}em")
    if e.spacing != "auto":
        args.append(f"spacing: {_typst_list_spacing(e.spacing)}")
    return f"#set terms({', '.join(args)})"


def _outline_line(e: OutlineStyle) -> str:
    args: list[str] = []
    if e.depth is not None:
        args.append(f"depth: {e.depth}")
    if e.indent != "auto":
        args.append(f"indent: {e.indent}")
    if not args:
        return ""
    return f"#set outline({', '.join(args)})"


# ---------------------------------------------------------------------------
# Heading level styles: show-set (set text) или it => { set block; set text; it }
# outlined/bookmarked/offset требуют heading(...) → рекурсия, не используем.
# ---------------------------------------------------------------------------


def _heading_level_line(hl: "HeadingLevelStyle") -> str:
    """Per-level: set text (и опц. set block). Возвращаем it — без создания нового heading."""
    level = hl.level
    parts: list[str] = []

    if level <= 2:
        above = "1.5em" if level == 1 else "1.2em"
        below = "1em" if level == 1 else "0.8em"
        parts.append(f"set block(above: {above}, below: {below})")

    if hl.text_override_style is not None:
        text_args = _text_override_to_typst_args(hl.text_override_style)
        parts.append(f"set text({', '.join(text_args)})")

    if not parts:
        return ""
    body = "; ".join(parts)
    return f"#show heading.where(level: {level}): it => {{ {body}; it }}"


def _equation_show_rule(e: "EquationStyle") -> str:
    """#show math.equation: set text(...) when equation has text override."""
    if e.text_override_style is None:
        return ""
    text_args = _text_override_to_typst_args(e.text_override_style)
    return f"#show math.equation: it => {{ set text({', '.join(text_args)}); it }}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_typst_preamble(profile: Profile) -> str:
    """Строит преамбулу Typst #set из стилей профиля. Один блок на элемент."""
    lines: list[str] = []

    _STYLE_BUILDERS = [
        (profile.page_style, _page_line),
        (profile.document_style, _document_line),
        (profile.par_style, _par_line),
        (profile.heading_style, _heading_line),
        (profile.bullet_list_style, _bullet_list_line),
        (profile.numbered_list_style, _numbered_list_line),
        (profile.table_style, _table_line),
        (profile.figure_style, _figure_line),
        (profile.footnote_style, _footnote_line),
        (profile.quote_style, _quote_line),
        (profile.raw_style, _raw_line),
        (profile.terms_style, _terms_line),
        (profile.outline_style, _outline_line),
    ]

    for style, builder in _STYLE_BUILDERS:
        if style is not None:
            part = builder(style)
            if part:
                lines.extend(part.split("\n"))

    # Heading level: set text + set block, возврат it
    if profile.heading_level_styles:
        for hl in sorted(profile.heading_level_styles, key=lambda x: x.level):
            line = _heading_level_line(hl)
            if line:
                lines.append(line)

    # Equation text override
    if profile.equation_style is not None:
        eq_part = _equation_show_rule(profile.equation_style)
        if eq_part:
            lines.append(eq_part)

    # Show-set rules for text override on elements (par, list, enum, etc.)
    _text_override_elements = [
        ("par", profile.par_style),
        ("list", profile.bullet_list_style),
        ("enum", profile.numbered_list_style),
        ("table.cell", profile.table_style),
        ("quote", profile.quote_style),
        ("raw", profile.raw_style),
        ("figure", profile.figure_style),
        ("footnote.entry", profile.footnote_style),
        ("terms", profile.terms_style),
        ("outline", profile.outline_style),
    ]
    for selector, style in _text_override_elements:
        line = _show_set_text_for_element(selector, style)
        if line:
            lines.append(line)

    return "\n".join(lines) + "\n" if lines else ""
