from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    elements: Mapped[list["ProfileElement"]] = relationship(
        "ProfileElement",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
