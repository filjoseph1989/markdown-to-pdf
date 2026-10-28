"""Markdown to HTML Conversion."""

import sys

try:
    from markdown_it import MarkdownIt
    HAS_MARKDOWN_IT = True
except ImportError:
    HAS_MARKDOWN_IT = False

try:
    import markdown
    HAS_MARKDOWN_LIB = True
except ImportError:
    HAS_MARKDOWN_LIB = False

INSTALL_HINT = (
    f"{sys.executable} -m pip install --user --break-system-packages markdown-it-py "
    "(the extra flags are needed on Homebrew Python; or install it in a virtualenv)"
)


def convert_markdown_to_html(md_text: str) -> str:
    """Convert Markdown text to HTML."""
    if HAS_MARKDOWN_IT:
        # CommonMark parses the way GitHub does: a list right after a line of text,
        # and fenced code inside list items, both render. Python-Markdown misses these.
        md = MarkdownIt("commonmark", {"html": True, "breaks": True}).enable(["table", "strikethrough"])
        return md.render(md_text)
    if HAS_MARKDOWN_LIB:
        print(
            "Warning: markdown-it-py is not installed, so lists directly under a line of text "
            f"and code blocks inside lists may not render. Install it with: {INSTALL_HINT}",
            file=sys.stderr,
        )
        extensions = [
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.toc",
            "markdown.extensions.nl2br",
            "markdown.extensions.sane_lists",
            "markdown.extensions.admonition",
        ]
        return markdown.markdown(md_text, extensions=extensions)

    print(
        "Warning: no Markdown library is installed, so tables, lists, bold text, links and "
        f"inline code will show as raw text. Install one with: {INSTALL_HINT}",
        file=sys.stderr,
    )
    return convert_markdown_minimal(md_text)


def convert_markdown_minimal(md_text: str) -> str:
    """Minimal pure Python fallback: headings, rules, paragraphs and fenced code only."""
    html_lines = []
    in_code_block = False

    for line in md_text.split("\n"):
        if line.startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                html_lines.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            continue

        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:].strip()}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.startswith("#### "):
            html_lines.append(f"<h4>{line[5:].strip()}</h4>")
        elif line.strip() == "---":
            html_lines.append("<hr>")
        elif line.strip():
            html_lines.append(f"<p>{line.strip()}</p>")

    return "\n".join(html_lines)
