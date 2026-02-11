from typing import Literal

from pydantic import BaseModel, Field


class FootnoteStyles(BaseModel):
    """GOST defaults for Typst footnote."""

    marker_format: Literal["1", "a", "A", "i", "I", "*"] = "1"


class FootnoteStylesUpdate(BaseModel):
    marker_format: Literal["1", "a", "A", "i", "I", "*"] | None = None
