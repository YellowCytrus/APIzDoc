"""
Generate Typst fragment for a title page. Insert between preamble and main document body.
When ignore_document_styles=True: wrap in block with #set overrides to isolate from preamble.
Output: #let for variables + place() calls (flow onto first page) + #pagebreak()
"""

from app.models.pydantic.page_editor import (
    Element,
    PaperSize,
    TextElement,
    VariableElement,
    LineElement,
)

TEXT_SIZE_PT = 12
VARIABLE_FONT_SIZE_PT = 10
TEXT_FILL = "black"
FONT_FAMILY = "Roboto"
VARIABLE_BOX_FILL = 'rgb("#ffffff")'
VARIABLE_BOX_STROKE = '0.5pt + rgb("#666666")'
DY_OFFSET_MM = 0


def _mm(x: float) -> str:
    v = round(x, 2)
    return f"{int(v)}mm" if v == int(v) else f"{v}mm"


def _escape_typst_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace("#", "\\#").replace("]", "\\]")


def _render_element(e: Element, variables: dict[str, str]) -> str:
    if isinstance(e, TextElement):
        content = _escape_typst_string(e.content)
        return (
            f"place(top + left, dx: {_mm(e.x_mm)}, dy: {_mm(e.y_mm + DY_OFFSET_MM)}, "
            f"[#text(size: {TEXT_SIZE_PT}pt)[{content}]])"
        )
    if isinstance(e, VariableElement):
        return (
            f"place(top + left, dx: {_mm(e.x_mm)}, dy: {_mm(e.y_mm + DY_OFFSET_MM)}, "
            f"box(width: {_mm(e.width_mm)}, height: auto, fill: {VARIABLE_BOX_FILL}, "
            f"stroke: {VARIABLE_BOX_STROKE}, "
            f"[#text(size: {VARIABLE_FONT_SIZE_PT}pt)[#{e.var_name}]]))"
        )
    if isinstance(e, LineElement):
        dx = e.x2_mm - e.x1_mm
        dy = e.y2_mm - e.y1_mm
        return (
            f"place(top + left, dx: {_mm(e.x1_mm)}, dy: {_mm(e.y1_mm + DY_OFFSET_MM)}, "
            f"line(end: ({_mm(dx)}, {_mm(dy)}), stroke: 1pt))"
        )
    raise TypeError(f"Unknown element type: {type(e)}")


_STYLE_OVERRIDES = """
  #set text(size: 12pt, font: "Roboto", fill: black)
  #set par(leading: 1.2em)
  #set list(marker: [—])
  #set enum(numbering: "1.")
  #set heading(numbering: none)
  #set figure(placement: auto)
  #set table(stroke: 0.5pt)
  #set strong(delta: 300)
"""


def generate_fragment(
    elements: list[Element],
    paper: PaperSize,
    variables: dict[str, str] | None = None,
    ignore_document_styles: bool = True,
) -> str:
    """
    Generate Typst fragment for insertion after preamble.
    When ignore_document_styles=True, wrap in block with #set overrides so the title page
    ignores all preamble styles (Typst has no unset; inner #set overrides outer until block end).
    """
    var_map = variables or {}
    place_calls = [_render_element(e, var_map) for e in elements]

    var_names = {e.var_name for e in elements if isinstance(e, VariableElement)}
    let_block = "\n".join(
        f"#let {name} = [{_escape_typst_string(var_map.get(name, ''))}]"
        for name in sorted(var_names)
    )
    if let_block:
        let_block += "\n"

    inner = "\n".join(f"#{p}" for p in place_calls)

    if ignore_document_styles and place_calls:
        # #page() isolates margins and numbering from preamble; body is positional
        body = f"{let_block}{_STYLE_OVERRIDES}  {inner}"
        page_content = (
            "#page(\n"
            "  margin: (top: 0pt, bottom: 0pt, left: 0pt, right: 0pt),\n"
            "  numbering: none,\n"
            "  header: none,\n"
            "  footer: none,\n"
            ")[\n"
            f"{body}\n"
            "]\n"
        )
    else:
        if let_block:
            page_content = let_block + "\n"
        else:
            page_content = ""
        if place_calls:
            page_content += inner + "\n"

    return f"{page_content}#pagebreak()\n"
