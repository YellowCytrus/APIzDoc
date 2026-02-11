import enum
from sqlalchemy import Boolean, Enum, Float, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import DefaultClause

from app.database import Base


class ElementType(str, enum.Enum):
    bullet_list = "bullet_list"
    document = "document"
    figure = "figure"
    footnote = "footnote"
    heading = "heading"
    numbered_list = "numbered_list"
    par = "par"
    quote = "quote"
    table = "table"


def _text_default(sql: str) -> DefaultClause:
    return DefaultClause(text(sql))


class ProfileElement(Base):
    __tablename__ = "profile_elements"
    __table_args__ = (UniqueConstraint("profile_id", "element_type", name="uq_profile_element_type"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    element_type: Mapped[ElementType] = mapped_column(
        Enum(ElementType, name="element_type_enum", create_constraint=True),
        nullable=False,
    )

    # Shared style columns (GOST defaults), all non-null
    tight: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=DefaultClause(text("true")))
    marker1: Mapped[str] = mapped_column(String(64), nullable=False, server_default=_text_default("'- '"))
    marker2: Mapped[str] = mapped_column(String(64), nullable=False, server_default=_text_default("'‣'"))
    marker3: Mapped[str] = mapped_column(String(64), nullable=False, server_default=_text_default("'–'"))
    indent_pt: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    body_indent_em: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
    spacing: Mapped[str] = mapped_column(String(32), nullable=False, server_default=_text_default("'auto'"))
    spacing_em: Mapped[float] = mapped_column(Float, nullable=False, server_default="1")
    font_size_pt: Mapped[float] = mapped_column(Float, nullable=False, server_default="12")
    line_spacing_em: Mapped[float] = mapped_column(Float, nullable=False, server_default="1.2")
    figure_width_em: Mapped[float] = mapped_column(Float, nullable=False, server_default="1")
    figure_height_em: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    table_stroke: Mapped[str] = mapped_column(String(32), nullable=False, server_default=_text_default("'0.5pt'"))
    heading_numbering: Mapped[str] = mapped_column(String(64), nullable=False, server_default=_text_default("'1.1.1'"))
    quote_indent_em: Mapped[float] = mapped_column(Float, nullable=False, server_default="1.5")
    footnote_marker_fmt: Mapped[str] = mapped_column(String(32), nullable=False, server_default=_text_default("'1'"))

    profile: Mapped["Profile"] = relationship("Profile", back_populates="elements")
