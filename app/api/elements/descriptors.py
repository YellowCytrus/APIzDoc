"""
Регистр дескрипторов элементов: декларативный список ORM-модель + Pydantic-схемы.
"""
from typing import Any

from app.api.elements.common import ElementDescriptor
from app.models.pydantic.bullet_list import BulletListStyles, BulletListStylesUpdate
from app.models.pydantic.document import DocumentStyles, DocumentStylesUpdate
from app.models.pydantic.figure import FigureStyles, FigureStylesUpdate
from app.models.pydantic.footnote import FootnoteStyles, FootnoteStylesUpdate
from app.models.pydantic.heading import HeadingStyles, HeadingStylesUpdate
from app.models.pydantic.numbered_list import NumberedListStyles, NumberedListStylesUpdate
from app.models.pydantic.outline_style import OutlineStyles, OutlineStylesUpdate
from app.models.pydantic.page import PageStyles, PageStylesUpdate
from app.models.pydantic.par import ParStyles, ParStylesUpdate
from app.models.pydantic.quote import QuoteStyles, QuoteStylesUpdate
from app.models.pydantic.raw import RawStyles, RawStylesUpdate
from app.models.pydantic.strong import StrongStyles, StrongStylesUpdate
from app.models.pydantic.table import TableStyles, TableStylesUpdate
from app.models.pydantic.terms import TermsStyles, TermsStylesUpdate
from app.models.sqlalchemy.styles import (
    BulletListStyle,
    DocumentStyle,
    FigureStyle,
    FootnoteStyle,
    HeadingStyle,
    NumberedListStyle,
    OutlineStyle,
    PageStyle,
    ParStyle,
    QuoteStyle,
    RawStyle,
    StrongStyle,
    TableStyle,
    TermsStyle,
)

ELEMENT_DESCRIPTORS: list[ElementDescriptor[Any, Any, Any]] = [
    ElementDescriptor(
        orm_model=BulletListStyle,
        path="bullet_list",
        tag="bullet_list",
        styles_model=BulletListStyles,
        styles_update_model=BulletListStylesUpdate,
        not_found_detail="Bullet list styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=DocumentStyle,
        path="document",
        tag="document",
        styles_model=DocumentStyles,
        styles_update_model=DocumentStylesUpdate,
        not_found_detail="Document styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=FigureStyle,
        path="figure",
        tag="figure",
        styles_model=FigureStyles,
        styles_update_model=FigureStylesUpdate,
        not_found_detail="Figure styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=FootnoteStyle,
        path="footnote",
        tag="footnote",
        styles_model=FootnoteStyles,
        styles_update_model=FootnoteStylesUpdate,
        not_found_detail="Footnote styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=HeadingStyle,
        path="heading",
        tag="heading",
        styles_model=HeadingStyles,
        styles_update_model=HeadingStylesUpdate,
        not_found_detail="Heading styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=NumberedListStyle,
        path="numbered_list",
        tag="numbered_list",
        styles_model=NumberedListStyles,
        styles_update_model=NumberedListStylesUpdate,
        not_found_detail="Numbered list styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=OutlineStyle,
        path="outline",
        tag="outline",
        styles_model=OutlineStyles,
        styles_update_model=OutlineStylesUpdate,
        not_found_detail="Outline styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=PageStyle,
        path="page",
        tag="page",
        styles_model=PageStyles,
        styles_update_model=PageStylesUpdate,
        not_found_detail="Page styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=ParStyle,
        path="par",
        tag="par",
        styles_model=ParStyles,
        styles_update_model=ParStylesUpdate,
        not_found_detail="Par styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=QuoteStyle,
        path="quote",
        tag="quote",
        styles_model=QuoteStyles,
        styles_update_model=QuoteStylesUpdate,
        not_found_detail="Quote styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=RawStyle,
        path="raw",
        tag="raw",
        styles_model=RawStyles,
        styles_update_model=RawStylesUpdate,
        not_found_detail="Raw styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=StrongStyle,
        path="strong",
        tag="strong",
        styles_model=StrongStyles,
        styles_update_model=StrongStylesUpdate,
        not_found_detail="Strong styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=TableStyle,
        path="table",
        tag="table",
        styles_model=TableStyles,
        styles_update_model=TableStylesUpdate,
        not_found_detail="Table styles not set for this profile",
    ),
    ElementDescriptor(
        orm_model=TermsStyle,
        path="terms",
        tag="terms",
        styles_model=TermsStyles,
        styles_update_model=TermsStylesUpdate,
        not_found_detail="Terms styles not set for this profile",
    ),
]
