"""
Compile Typst source to PDF via typst CLI.
"""
import asyncio
import subprocess
import tempfile
from pathlib import Path


class TypstCompileError(Exception):
    """Typst compilation failed."""

    def __init__(self, message: str, stderr: str = "") -> None:
        self.stderr = stderr
        super().__init__(message)


def _compile_typst_to_pdf_sync(source: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        inp = root / "input.typ"
        out = root / "output.pdf"
        inp.write_text(source, encoding="utf-8")
        result = subprocess.run(
            ["typst", "compile", str(inp), str(out)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
            cwd=tmpdir,
        )
        if result.returncode != 0:
            raise TypstCompileError(
                f"Typst exited with code {result.returncode}",
                stderr=result.stderr or "",
            )
        return out.read_bytes()


async def compile_typst_to_pdf(source: str) -> bytes:
    """Compile Typst source to PDF bytes. Raises TypstCompileError on failure."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _compile_typst_to_pdf_sync, source)
