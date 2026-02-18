"""
Компиляция исходников Typst в PDF через CLI typst.
"""

import asyncio
import subprocess
import tempfile
from pathlib import Path


class TypstCompileError(Exception):
    """Ошибка компиляции Typst."""

    def __init__(self, message: str, stderr: str = "") -> None:
        self.stderr = stderr
        super().__init__(message)


def _compile_typst_to_pdf_sync(source: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        inp = root / "input.typ"
        out = root / "output.pdf"
        inp.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                ["typst", "compile", str(inp), str(out)],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                cwd=tmpdir,
            )
        except subprocess.TimeoutExpired as exc:
            raise TypstCompileError(
                "Typst timed out",
                stderr="Process exceeded 60s timeout",
            ) from exc
        if result.returncode != 0:
            raise TypstCompileError(
                f"Typst exited with code {result.returncode}",
                stderr=result.stderr or "",
            )
        return out.read_bytes()


async def compile_typst_to_pdf(source: str) -> bytes:
    """Компилирует исходник Typst в байты PDF. При ошибке выбрасывает TypstCompileError."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _compile_typst_to_pdf_sync, source)
