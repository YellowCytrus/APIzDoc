from typing import Optional

from pydantic import BaseModel, Field


class PageStyles(BaseModel):
    """Стили страницы Typst: #set page(...)."""

    paper: str = Field("a4", max_length=64, description="Формат бумаги")
    flipped: bool = Field(False, description="Альбомная ориентация")
    margin_top: float = Field(2.5, ge=0.0, description="Верхнее поле в cm")
    margin_bottom: float = Field(2.5, ge=0.0, description="Нижнее поле в cm")
    margin_left: float = Field(2.5, ge=0.0, description="Левое поле в cm")
    margin_right: float = Field(2.5, ge=0.0, description="Правое поле в cm")
    columns: int = Field(1, ge=1, le=10, description="Количество колонок")
    numbering: str = Field("none", max_length=64, description="Нумерация страниц ('none' = нет)")
    number_align: str = Field("center+bottom", max_length=32, description="Позиция номера")


class PageStylesUpdate(BaseModel):
    paper: Optional[str] = Field(None, max_length=64)
    flipped: Optional[bool] = None
    margin_top: Optional[float] = Field(None, ge=0.0)
    margin_bottom: Optional[float] = Field(None, ge=0.0)
    margin_left: Optional[float] = Field(None, ge=0.0)
    margin_right: Optional[float] = Field(None, ge=0.0)
    columns: Optional[int] = Field(None, ge=1, le=10)
    numbering: Optional[str] = Field(None, max_length=64)
    number_align: Optional[str] = Field(None, max_length=32)
