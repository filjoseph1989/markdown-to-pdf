# markdown-to-pdf

Convert Markdown (`.md`) documents to clean, print-ready PDFs using a headless browser.

## Features

- GitHub-Flavored Markdown: tables, task lists, fenced code, strikethrough
- GitHub Alerts: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`
- LaTeX math: `$...$` inline and `$$...$$` display, rendered with KaTeX
- Local images resolved relative to the Markdown file
- YAML frontmatter rendered at the top of the document
- Page size (A4, Letter, Legal), margins and landscape orientation
- Single file or a whole directory at once

## Requirements

- Python 3.9+
- A renderer, tried in this order:
  1. Google Chrome, Brave, Microsoft Edge or Chromium (recommended)
  2. [WeasyPrint](https://weasyprint.org/)
  3. [wkhtmltopdf](https://wkhtmltopdf.org/)
- [markdown-it-py](https://github.com/executablebooks/markdown-it-py) (recommended):

  ```bash
  python3 -m pip install markdown-it-py
  ```

  Without it, Python-Markdown is used if installed (some nested lists and code blocks may not
  render), and as a last resort a bare converter that handles only headings and paragraphs.
- Internet access when the document contains math (KaTeX loads from a CDN).

## Installation

The repository is the Python package itself, so clone it into a folder named `md_to_pdf`:

```bash
git clone https://github.com/filjoseph1989/markdown-to-pdf.git md_to_pdf
```

## Usage

Run it from the folder that contains `md_to_pdf`:

```bash
# Single file -> notes.pdf next to notes.md
python3 md_to_pdf notes.md

# Choose the output path
python3 md_to_pdf notes.md -o ~/Desktop/notes.pdf

# Letter size, landscape, wider margins, open when done (macOS)
python3 md_to_pdf report.md --page-size Letter --landscape --margin 25mm --open

# Every .md file in a directory
python3 md_to_pdf docs/
```

`python3 -m md_to_pdf ...` works too.

### Options

| Option | Description | Default |
|---|---|---|
| `input` | Markdown file or directory of Markdown files | — |
| `-o`, `--output` | Output PDF path (for a directory input: an existing output directory) | Same name, `.pdf` |
| `--page-size` | `A4`, `Letter` or `Legal` | `A4` |
| `--margin` | CSS page margin, e.g. `20mm` | `18mm` |
| `--landscape` | Landscape orientation | Off |
| `--browser` | Path to a Chrome/Chromium/Brave/Edge executable | Auto-detected |
| `--keep-html` | Keep the intermediate HTML file for debugging | Off |
| `--open` | Open the PDF after conversion (macOS only) | Off |

### From Python

```python
from pathlib import Path
from md_to_pdf import render_markdown_file

render_markdown_file(Path("notes.md"), page_size="Letter", landscape=True)
```

## How it works

Markdown → HTML → PDF:

| Module | Role |
|---|---|
| `cli.py` | Command-line arguments; single file vs. directory |
| `converter.py` | The pipeline |
| `preprocess.py` | Frontmatter, GitHub alerts, task lists, relative images |
| `latex.py` | Protects `$...$` math from Markdown and hands it to KaTeX |
| `md_html.py` | Markdown → HTML (markdown-it-py, Python-Markdown, or bare fallback) |
| `template.py` | Builds the full HTML page |
| `styles.css` | All PDF styling — edit this to change the look |
| `renderers.py` | Finds a browser and prints the HTML to PDF |
