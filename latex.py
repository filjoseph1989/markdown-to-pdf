"""LaTeX Math: protect from Markdown, restore as KaTeX-renderable elements."""

import html as html_lib
import re

# Code blocks/spans are matched first so `$` inside code is never treated as math
MATH_PATTERN = re.compile(
    r"(?P<fence>^(`{3,}|~{3,}).*?^\2)"
    r"|(?P<code>`+[^`\n]*?`+)"
    r"|\$\$(?P<display>.+?)\$\$"
    r"|(?<![\\$\w])\$(?!\s)(?P<inline>[^$\n]+?)(?<![\s\\])\$(?![\w$])",
    re.MULTILINE | re.DOTALL,
)

KATEX_HEAD = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".math").forEach(function (el) {
        katex.render(el.textContent, el, {
            displayMode: el.classList.contains("math-display"),
            throwOnError: false,
        });
    });
});
</script>
"""


def protect_math(text: str) -> tuple[str, list[tuple[str, bool]]]:
    """Swap math for alphanumeric placeholders so Markdown leaves the LaTeX untouched."""
    formulas: list[tuple[str, bool]] = []

    def repl(match):
        if match.group("fence") or match.group("code"):
            return match.group(0)
        is_display = match.group("display") is not None
        formulas.append((match.group("display" if is_display else "inline").strip(), is_display))
        return f"MATHPLACEHOLDER{len(formulas) - 1}END"

    return MATH_PATTERN.sub(repl, text), formulas


def restore_math(html_text: str, formulas: list[tuple[str, bool]]) -> str:
    """Replace placeholders with elements that KaTeX renders in the browser."""
    for idx, (tex, is_display) in enumerate(formulas):
        token = f"MATHPLACEHOLDER{idx}END"
        escaped = html_lib.escape(tex)
        if is_display:
            element = f'<div class="math math-display">{escaped}</div>'
            html_text = html_text.replace(f"<p>{token}</p>", element)
        else:
            element = f'<span class="math math-inline">{escaped}</span>'
        html_text = html_text.replace(token, element)
    return html_text
