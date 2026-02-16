"""
Преобразование Markdown в Typst через подпроцесс pandoc.
"""
import asyncio
import subprocess
from typing import Any


class PandocError(Exception):
    """Ошибка преобразования Pandoc."""

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
    """Преобразует байты Markdown в строку исходного кода Typst. При ошибке выбрасывает PandocError."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _markdown_to_typst_sync, markdown)
