"""The conversion pipeline: Markdown file -> HTML page -> PDF."""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .latex import protect_math, restore_math
from .md_html import convert_markdown_to_html
from .preprocess import preprocess_markdown
from .renderers import (
    find_chromium_executable,
    generate_pdf_with_chromium,
    generate_pdf_with_weasyprint,
    generate_pdf_with_wkhtmltopdf,
)
from .template import build_html


def render_markdown_file(
    input_file: Path,
    output_pdf: Optional[Path] = None,
    page_size: str = "A4",
    margin: str = "18mm",
    landscape: bool = False,
    custom_browser: Optional[str] = None,
    keep_html: bool = False,
    open_after: bool = False,
) -> Path:
    """Convert a single Markdown file to PDF."""
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if output_pdf is None:
        output_pdf = input_file.with_suffix(".pdf")

    # Read and pre-process Markdown
    md_content = input_file.read_text(encoding="utf-8")
    protected_md, formulas = protect_math(md_content)
    processed_md = preprocess_markdown(protected_md, base_dir=input_file.parent)

    # Convert to HTML
    body_html = restore_math(convert_markdown_to_html(processed_md), formulas)

    # Prepare document title
    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else input_file.stem

    full_html = build_html(
        title=doc_title,
        body=body_html,
        page_size=page_size,
        margin=margin,
        landscape=landscape,
        with_math=bool(formulas),
    )

    # Write temporary HTML file
    temp_html = input_file.parent / f"._{input_file.stem}_temp.html"
    temp_html.write_text(full_html, encoding="utf-8")

    try:
        # Determine rendering engine
        browser_bin = custom_browser or find_chromium_executable()
        success = False

        if browser_bin:
            success = generate_pdf_with_chromium(
                temp_html,
                output_pdf,
                browser_bin=browser_bin,
                landscape=landscape,
            )

        if not success:
            success = generate_pdf_with_weasyprint(temp_html, output_pdf)

        if not success:
            success = generate_pdf_with_wkhtmltopdf(temp_html, output_pdf)

        if not success:
            raise RuntimeError(
                "Failed to render PDF. No compatible renderer found. "
                "Please install Google Chrome, Brave, Microsoft Edge, Chromium, or WeasyPrint."
            )

    finally:
        if not keep_html and temp_html.exists():
            temp_html.unlink()

    if open_after and sys.platform == "darwin":
        subprocess.run(["open", str(output_pdf)])

    return output_pdf
