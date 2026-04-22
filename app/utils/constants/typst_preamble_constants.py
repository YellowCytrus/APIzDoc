"""Constants for Typst preamble generation."""

import re

# Typst reserves numbering space for hidden heading numbers.
# We compensate with a negative left inset when numbering is disabled.
HEADING_UNNUMBERED_LEFT_OUTDENT = "-0.3em"

# Placeholders accepted in figure caption template.
CAPTION_PLACEHOLDER_RE = re.compile(r"\{([h][1-6]|[N]|content)\}", re.IGNORECASE)

# Font families that Typst may not have installed mapped to safe built-ins.
FONT_ALIASES: dict[str, str] = {
    "times new roman": "Libertinus Serif",
    "times": "Libertinus Serif",
    "arial": "DejaVu Sans",
    "helvetica": "DejaVu Sans",
    "courier new": "DejaVu Sans Mono",
    "courier": "DejaVu Sans Mono",
}

