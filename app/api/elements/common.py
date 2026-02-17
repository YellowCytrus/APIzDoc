"""
Общие типы для роутеров элементов: ElementDescriptor.
"""
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

TModel = TypeVar("TModel")
TStyles = TypeVar("TStyles")
TStylesUpdate = TypeVar("TStylesUpdate")


@dataclass(frozen=True)
class ElementDescriptor(Generic[TModel, TStyles, TStylesUpdate]):
    """Дескриптор типа элемента: ORM-модель, Pydantic-схемы, путь и тег."""

    orm_model: type[TModel]
    path: str
    tag: str
    styles_model: type[TStyles]
    styles_update_model: type[TStylesUpdate]
    not_found_detail: str
