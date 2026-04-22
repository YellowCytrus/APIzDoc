from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.constants.style_defaults import LIST_BODY_INDENT_MM_DEFAULT
from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class NumberedListStyles(BaseModel):
    """Стили нумерованного списка Typst: #set enum(...)."""

    tight: bool = True
    indent: float = Field(0.0, ge=0.0, description="Отступ в mm")
    body_indent: float = Field(LIST_BODY_INDENT_MM_DEFAULT, ge=0.0, description="Отступ тела в mm")
    spacing: Literal["auto", "tight", "loose"] = "auto"
    numbering: str = Field("1.", max_length=64, description="Шаблон нумерации")
    start: Optional[int] = Field(None, ge=0, description="Начальный номер (null = auto)")
    full: bool = Field(False, description="Полная нумерация родительских уровней")
    reversed: bool = Field(False, description="Обратный порядок нумерации")
    number_align: str = Field("end+top", max_length=32, description="Выравнивание номера")
    text_override: Optional[TextOverrideStyles] = None


class NumberedListStylesUpdate(BaseModel):
    tight: Optional[bool] = None
    indent: Optional[float] = Field(None, ge=0.0)
    body_indent: Optional[float] = Field(None, ge=0.0)
    spacing: Optional[Literal["auto", "tight", "loose"]] = None
    numbering: Optional[str] = Field(None, max_length=64)
    start: Optional[int] = Field(None, ge=0)
    full: Optional[bool] = None
    reversed: Optional[bool] = None
    number_align: Optional[str] = Field(None, max_length=32)
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
