from typing import Literal, Optional

from pydantic import BaseModel, Field


class ParStyles(BaseModel):
    """Стили абзаца Typst: #set par(...)."""

    spacing: float = Field(1.0, ge=0.0, description="Интервал между абзацами в em")
    first_line_indent: float = Field(0.0, ge=0.0, description="Отступ первой строки в em")
    hanging_indent: float = Field(0.0, ge=0.0, description="Висячий отступ в em")
    justify: bool = Field(False, description="Выравнивание по ширине")
    linebreaks: Literal["auto", "simple", "optimized"] = "auto"


class ParStylesUpdate(BaseModel):
    spacing: Optional[float] = Field(None, ge=0.0)
    first_line_indent: Optional[float] = Field(None, ge=0.0)
    hanging_indent: Optional[float] = Field(None, ge=0.0)
    justify: Optional[bool] = None
    linebreaks: Optional[Literal["auto", "simple", "optimized"]] = None
