from pydantic import BaseModel, Field


class TableStyles(BaseModel):
    """Значения по умолчанию ГОСТ для таблицы Typst."""

    stroke: str = Field("0.5pt", max_length=32, description="Толщина линии, напр. '0.5pt'")


class TableStylesUpdate(BaseModel):
    stroke: str | None = Field(None, max_length=32)
