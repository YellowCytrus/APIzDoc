"""Роутеры стилей элементов: генерируются фабрикой из дескрипторов."""
from fastapi import APIRouter

from app.api.elements.descriptors import ELEMENT_DESCRIPTORS
from app.api.elements.factory import create_element_router


def get_element_routers() -> list[APIRouter]:
    """Возвращает список роутеров для всех типов элементов."""
    return [create_element_router(d) for d in ELEMENT_DESCRIPTORS]
