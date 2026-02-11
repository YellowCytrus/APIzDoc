"""
Convert Markdown to Typst via pandoc subprocess.
"""
import asyncio
import subprocess
from typing import Any


class PandocError(Exception):
    """Pandoc conversion failed."""

    def __init__(self, message: str, stderr: str = "") -> None:
        self.stderr = stderr
        super().__init__(message)


def _markdown_to_typst_sync(markdown: bytes) -> str:
    result = subprocess.run(
        ["pandoc", "--from=markdown+raw_attribute", "--to=typst", "--output=-"],
        input=markdown,
        capture_output=True,
        text=False,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        raise PandocError(f"Pandoc exited with code {result.returncode}", stderr=stderr)
    return (result.stdout or b"").decode("utf-8")


async def markdown_to_typst(markdown: bytes) -> str:
    """Convert Markdown bytes to Typst source string. Raises PandocError on failure."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _markdown_to_typst_sync, markdown)
