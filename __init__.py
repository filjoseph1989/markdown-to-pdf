"""
Convert Markdown (.md) documents to high-quality PDF files.

Supports:
- Full GitHub-Flavored Markdown (GFM) including tables, task lists, fenced code blocks
- GitHub Alerts (> [!NOTE], > [!TIP], > [!IMPORTANT], > [!WARNING], > [!CAUTION])
- LaTeX math ($...$ inline, $$...$$ display) rendered with KaTeX (needs internet for the CDN)
- Local image resolution relative to the Markdown source file
- YAML frontmatter rendering
- Customizable page size (A4, Letter, Legal), margins, and orientation
- Uses headless Google Chrome, Brave, Edge, Chromium, or WeasyPrint/wkhtmltopdf
- Single file or batch directory conversion

Requires markdown-it-py (`python3 -m pip install markdown-it-py`). Python-Markdown is used
when it's missing, and a bare fallback (headings and paragraphs only) when neither is installed.

Modules:
- cli.py         command-line arguments, single file vs. directory
- converter.py   the pipeline: Markdown -> HTML -> PDF
- preprocess.py  frontmatter, GitHub alerts, task lists, relative images
- latex.py       protects $...$ math from Markdown and hands it to KaTeX
- md_html.py     Markdown -> HTML (markdown-it-py, Python-Markdown, or bare fallback)
- template.py    builds the full HTML page from styles.css
- styles.css     all PDF styling
- renderers.py   finds a browser and prints the HTML to PDF
"""

from .converter import render_markdown_file

__all__ = ["render_markdown_file"]
