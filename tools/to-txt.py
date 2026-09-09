"""Извлекает текст из PDF-файла и сохраняет его в .txt рядом с источником.

Использование:
    python to-txt.py <файл.pdf> [ещё.pdf ...]
"""

import sys
from pathlib import Path

from pypdf import PdfReader


def pdf_to_txt(pdf_path: Path) -> Path:
    reader = PdfReader(str(pdf_path))
    parts = []
    for i, page in enumerate(reader.pages):
        parts.append(f"===== PAGE {i + 1} =====")
        parts.append(page.extract_text() or "")
    txt_path = pdf_path.with_suffix(".txt")
    txt_path.write_text("\n".join(parts), encoding="utf-8")
    return txt_path


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Укажите хотя бы один PDF-файл")
    for arg in sys.argv[1:]:
        pdf_path = Path(arg)
        txt_path = pdf_to_txt(pdf_path)
        print(f"{pdf_path.name} -> {txt_path.name}")


if __name__ == "__main__":
    main()
