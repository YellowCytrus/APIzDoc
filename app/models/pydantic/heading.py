from pydantic import BaseModel, Field


class HeadingStyles(BaseModel):
    """Значения по умолчанию ГОСТ для заголовка Typst."""

    numbering: str = Field("1.1.1", max_length=64, description="Шаблон нумерации или 'none'")


class HeadingStylesUpdate(BaseModel):
    numbering: str | None = Field(None, max_length=64)
