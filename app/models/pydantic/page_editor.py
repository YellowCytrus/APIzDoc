"""Pydantic models for page editor (title pages). Compatible with PIZDoCanvas."""

from typing import Any, Literal, Optional, Union

from pydantic import BaseModel


class PaperSize(BaseModel):
    """Paper dimensions and margin (mm)."""

    name: str = "a4"
    width: float = 210.0
    height: float = 297.0
    margin: float = 20.0


class TextElement(BaseModel):
    """Static text element."""

    type: Literal["text"] = "text"
    id: str
    x_mm: float
    y_mm: float
    content: str = "Sample Text"
    text_style: Optional[dict[str, Any]] = None


class VariableElement(BaseModel):
    """Editable variable with drag + resize."""

    type: Literal["variable"] = "variable"
    id: str
    x_mm: float
    y_mm: float
    width_mm: float = 50.0
    height_lines: float = 2.0
    var_name: str = "var"
    text_style: Optional[dict[str, Any]] = None


class LineElement(BaseModel):
    """Line with endpoints (x1,y1,x2,y2 mm)."""

    type: Literal["line"] = "line"
    id: str
    x1_mm: float
    y1_mm: float
    x2_mm: float
    y2_mm: float


Element = Union[TextElement, VariableElement, LineElement]


class TitlePageContent(BaseModel):
    """Content of a title page: elements, paper, variables."""

    elements: list[Element]
    paper: PaperSize
    variables: dict[str, str] = {}
    ignore_document_styles: bool = True
