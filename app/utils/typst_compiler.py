"""
Компиляция исходников Typst в PDF через CLI typst.
Поддержка локальных изображений: пути вида images/... копируются в tmpdir перед компиляцией.
"""

import asyncio
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


class TypstCompileError(Exception):
    """Ошибка компиляции Typst."""

    def __init__(self, message: str, stderr: str = "") -> None:
        self.stderr = stderr
        super().__init__(message)


def _extract_image_paths(typst_source: str) -> list[str]:
    """Извлекает локальные пути к изображениям из typst: image("path") или image("path", ...)."""
    matches = re.findall(r'image\s*\(\s*"([^"]+)"', typst_source)
    # Только локальные пути (не http/https, не data:)
    return [p for p in matches if not p.startswith(("http://", "https://", "data:"))]


def _compile_typst_to_pdf_sync(source: str, images_dir: Path | None = None) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        inp = root / "input.typ"
        out = root / "output.pdf"
        inp.write_text(source, encoding="utf-8")

        # Копируем локальные изображения в tmpdir
        if images_dir is not None and images_dir.exists():
            for rel_path in _extract_image_paths(source):
                # Поддержка только путей images/xxx, без path traversal
                if not rel_path.startswith("images/") or ".." in rel_path:
                    continue
                src_file = images_dir / Path(rel_path).name
                if src_file.exists() and src_file.is_file():
                    dst_subdir = root / Path(rel_path).parent
                    dst_subdir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, root / rel_path)

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


async def compile_typst_to_pdf(
    source: str,
    images_dir: Path | None = None,
) -> bytes:
    """Компилирует исходник Typst в байты PDF. При ошибке выбрасывает TypstCompileError.
    images_dir: корень проекта, откуда берутся файлы images/... (по умолчанию None)."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _compile_typst_to_pdf_sync(source, images_dir))
