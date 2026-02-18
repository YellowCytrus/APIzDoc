"""Роутеры стилей элементов: генерируются фабрикой из дескрипторов."""

from fastapi import APIRouter

from app.api.elements.descriptors import ELEMENT_DESCRIPTORS
from app.api.elements.factory import create_element_router
from app.api.elements.heading_levels import router as heading_levels_router


def get_element_routers() -> list[APIRouter]:
    """Возвращает список роутеров для всех типов элементов."""
    routers = [create_element_router(d) for d in ELEMENT_DESCRIPTORS]
    routers.append(heading_levels_router)
    return routers
