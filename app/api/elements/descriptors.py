"""
Регистр дескрипторов элементов: маппинг ORM -> DTO для каждого типа элемента.
"""
from typing import Any

from app.api.elements.common import ElementDescriptor
from app.models.pydantic.bullet_list import BulletListStyles, BulletListStylesUpdate
from app.models.pydantic.document import DocumentStyles, DocumentStylesUpdate
from app.models.pydantic.figure import FigureStyles, FigureStylesUpdate
from app.models.pydantic.footnote import FootnoteStyles, FootnoteStylesUpdate
from app.models.pydantic.heading import HeadingStyles, HeadingStylesUpdate
from app.models.pydantic.numbered_list import NumberedListStyles, NumberedListStylesUpdate
from app.models.pydantic.par import ParStyles, ParStylesUpdate
from app.models.pydantic.quote import QuoteStyles, QuoteStylesUpdate
from app.models.pydantic.table import TableStyles, TableStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

_DEFAULT_MARKERS = ["- ", "‣", "–"]


def _bullet_list_to_dto(row: ProfileElement) -> BulletListStyles:
    return BulletListStyles(
        tight=row.tight,
        marker=[row.marker1, row.marker2, row.marker3],
        indent=row.indent_pt,
        body_indent=row.body_indent_em,
        spacing=row.spacing,
    )


def _bullet_list_apply_full(row: ProfileElement, body: BulletListStyles) -> None:
    row.tight = body.tight
    markers = (body.marker + _DEFAULT_MARKERS)[:3]
    row.marker1, row.marker2, row.marker3 = markers[0], markers[1], markers[2]
    row.indent_pt = body.indent
    row.body_indent_em = body.body_indent
    row.spacing = body.spacing


def _bullet_list_apply_partial(row: ProfileElement, body: BulletListStylesUpdate) -> None:
    if body.tight is not None:
        row.tight = body.tight
    if body.marker is not None:
        markers = (body.marker + _DEFAULT_MARKERS)[:3]
        row.marker1, row.marker2, row.marker3 = markers[0], markers[1], markers[2]
    if body.indent is not None:
        row.indent_pt = body.indent
    if body.body_indent is not None:
        row.body_indent_em = body.body_indent
    if body.spacing is not None:
        row.spacing = body.spacing


def _document_to_dto(row: ProfileElement) -> DocumentStyles:
    return DocumentStyles(
        font_size=row.font_size_pt,
        line_spacing=row.line_spacing_em,
    )


def _document_apply_full(row: ProfileElement, body: DocumentStyles) -> None:
    row.font_size_pt = body.font_size
    row.line_spacing_em = body.line_spacing


def _document_apply_partial(row: ProfileElement, body: DocumentStylesUpdate) -> None:
    if body.font_size is not None:
        row.font_size_pt = body.font_size
    if body.line_spacing is not None:
        row.line_spacing_em = body.line_spacing


def _figure_to_dto(row: ProfileElement) -> FigureStyles:
    return FigureStyles(
        width=row.figure_width_em,
        height=row.figure_height_em,
    )


def _figure_apply_full(row: ProfileElement, body: FigureStyles) -> None:
    row.figure_width_em = body.width
    row.figure_height_em = body.height


def _figure_apply_partial(row: ProfileElement, body: FigureStylesUpdate) -> None:
    if body.width is not None:
        row.figure_width_em = body.width
    if body.height is not None:
        row.figure_height_em = body.height


def _footnote_to_dto(row: ProfileElement) -> FootnoteStyles:
    return FootnoteStyles(marker_format=row.footnote_marker_fmt)


def _footnote_apply_full(row: ProfileElement, body: FootnoteStyles) -> None:
    row.footnote_marker_fmt = body.marker_format


def _footnote_apply_partial(row: ProfileElement, body: FootnoteStylesUpdate) -> None:
    if body.marker_format is not None:
        row.footnote_marker_fmt = body.marker_format


def _heading_to_dto(row: ProfileElement) -> HeadingStyles:
    return HeadingStyles(numbering=row.heading_numbering)


def _heading_apply_full(row: ProfileElement, body: HeadingStyles) -> None:
    row.heading_numbering = body.numbering


def _heading_apply_partial(row: ProfileElement, body: HeadingStylesUpdate) -> None:
    if body.numbering is not None:
        row.heading_numbering = body.numbering


def _numbered_list_to_dto(row: ProfileElement) -> NumberedListStyles:
    return NumberedListStyles(
        tight=row.tight,
        indent=row.indent_pt,
        body_indent=row.body_indent_em,
        spacing=row.spacing,
    )


def _numbered_list_apply_full(row: ProfileElement, body: NumberedListStyles) -> None:
    row.tight = body.tight
    row.indent_pt = body.indent
    row.body_indent_em = body.body_indent
    row.spacing = body.spacing


def _numbered_list_apply_partial(row: ProfileElement, body: NumberedListStylesUpdate) -> None:
    if body.tight is not None:
        row.tight = body.tight
    if body.indent is not None:
        row.indent_pt = body.indent
    if body.body_indent is not None:
        row.body_indent_em = body.body_indent
    if body.spacing is not None:
        row.spacing = body.spacing


def _par_to_dto(row: ProfileElement) -> ParStyles:
    return ParStyles(spacing=row.spacing_em)


def _par_apply_full(row: ProfileElement, body: ParStyles) -> None:
    row.spacing_em = body.spacing


def _par_apply_partial(row: ProfileElement, body: ParStylesUpdate) -> None:
    if body.spacing is not None:
        row.spacing_em = body.spacing


def _quote_to_dto(row: ProfileElement) -> QuoteStyles:
    return QuoteStyles(indent=row.quote_indent_em)


def _quote_apply_full(row: ProfileElement, body: QuoteStyles) -> None:
    row.quote_indent_em = body.indent


def _quote_apply_partial(row: ProfileElement, body: QuoteStylesUpdate) -> None:
    if body.indent is not None:
        row.quote_indent_em = body.indent


def _table_to_dto(row: ProfileElement) -> TableStyles:
    return TableStyles(stroke=row.table_stroke)


def _table_apply_full(row: ProfileElement, body: TableStyles) -> None:
    row.table_stroke = body.stroke


def _table_apply_partial(row: ProfileElement, body: TableStylesUpdate) -> None:
    if body.stroke is not None:
        row.table_stroke = body.stroke


ELEMENT_DESCRIPTORS: list[ElementDescriptor[Any, Any]] = [
    ElementDescriptor(
        element_type=ElementType.bullet_list,
        path="bullet_list",
        tag="bullet_list",
        styles_model=BulletListStyles,
        styles_update_model=BulletListStylesUpdate,
        to_dto=_bullet_list_to_dto,
        apply_full=_bullet_list_apply_full,
        apply_partial=_bullet_list_apply_partial,
        not_found_detail="Bullet list styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.document,
        path="document",
        tag="document",
        styles_model=DocumentStyles,
        styles_update_model=DocumentStylesUpdate,
        to_dto=_document_to_dto,
        apply_full=_document_apply_full,
        apply_partial=_document_apply_partial,
        not_found_detail="Document styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.figure,
        path="figure",
        tag="figure",
        styles_model=FigureStyles,
        styles_update_model=FigureStylesUpdate,
        to_dto=_figure_to_dto,
        apply_full=_figure_apply_full,
        apply_partial=_figure_apply_partial,
        not_found_detail="Figure styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.footnote,
        path="footnote",
        tag="footnote",
        styles_model=FootnoteStyles,
        styles_update_model=FootnoteStylesUpdate,
        to_dto=_footnote_to_dto,
        apply_full=_footnote_apply_full,
        apply_partial=_footnote_apply_partial,
        not_found_detail="Footnote styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.heading,
        path="heading",
        tag="heading",
        styles_model=HeadingStyles,
        styles_update_model=HeadingStylesUpdate,
        to_dto=_heading_to_dto,
        apply_full=_heading_apply_full,
        apply_partial=_heading_apply_partial,
        not_found_detail="Heading styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.numbered_list,
        path="numbered_list",
        tag="numbered_list",
        styles_model=NumberedListStyles,
        styles_update_model=NumberedListStylesUpdate,
        to_dto=_numbered_list_to_dto,
        apply_full=_numbered_list_apply_full,
        apply_partial=_numbered_list_apply_partial,
        not_found_detail="Numbered list styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.par,
        path="par",
        tag="par",
        styles_model=ParStyles,
        styles_update_model=ParStylesUpdate,
        to_dto=_par_to_dto,
        apply_full=_par_apply_full,
        apply_partial=_par_apply_partial,
        not_found_detail="Par styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.quote,
        path="quote",
        tag="quote",
        styles_model=QuoteStyles,
        styles_update_model=QuoteStylesUpdate,
        to_dto=_quote_to_dto,
        apply_full=_quote_apply_full,
        apply_partial=_quote_apply_partial,
        not_found_detail="Quote styles not set for this profile",
    ),
    ElementDescriptor(
        element_type=ElementType.table,
        path="table",
        tag="table",
        styles_model=TableStyles,
        styles_update_model=TableStylesUpdate,
        to_dto=_table_to_dto,
        apply_full=_table_apply_full,
        apply_partial=_table_apply_partial,
        not_found_detail="Table styles not set for this profile",
    ),
]
