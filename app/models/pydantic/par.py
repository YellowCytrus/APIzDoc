from pydantic import BaseModel, Field


class ParStyles(BaseModel):
    """Значения по умолчанию ГОСТ для абзаца Typst."""

    spacing: float = Field(1.0, ge=0.0, description="Межстрочный интервал абзаца в em")


class ParStylesUpdate(BaseModel):
    spacing: float | None = Field(None, ge=0.0)
