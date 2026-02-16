"""
Общие типы для роутеров элементов: ElementDescriptor и фабрика роутеров.
"""
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

T = TypeVar("T")
TUpdate = TypeVar("TUpdate")


@dataclass(frozen=True)
class ElementDescriptor(Generic[T, TUpdate]):
    """Дескриптор типа элемента: метаданные и функции маппинга ORM <-> DTO."""

    element_type: ElementType
    path: str
    tag: str
    styles_model: type[T]
    styles_update_model: type[TUpdate]
    to_dto: Callable[[ProfileElement], T]
    apply_full: Callable[[ProfileElement, T], None]
    apply_partial: Callable[[ProfileElement, TUpdate], None]
    not_found_detail: str
