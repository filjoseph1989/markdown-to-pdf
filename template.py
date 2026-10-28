"""HTML page template; the styling lives in styles.css next to this file."""

from pathlib import Path

from .latex import KATEX_HEAD

CSS_TEMPLATE_PATH = Path(__file__).with_name("styles.css")

HTML_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<style>
{{CSS}}
</style>
{{HEAD_EXTRA}}
</head>
<body>
{{BODY}}
</body>
</html>
"""


def build_css(page_size: str, margin: str, landscape: bool) -> str:
    orientation = "landscape" if landscape else "portrait"
    return (
        CSS_TEMPLATE_PATH.read_text(encoding="utf-8")
        .replace("{{PAGE_SIZE}}", page_size)
        .replace("{{ORIENTATION}}", orientation)
        .replace("{{MARGIN}}", margin)
    )


def build_html(
    title: str,
    body: str,
    page_size: str,
    margin: str,
    landscape: bool,
    with_math: bool,
) -> str:
    return (
        HTML_WRAPPER
        .replace("{{TITLE}}", title)
        .replace("{{CSS}}", build_css(page_size, margin, landscape))
        .replace("{{HEAD_EXTRA}}", KATEX_HEAD if with_math else "")
        .replace("{{BODY}}", body)
    )
