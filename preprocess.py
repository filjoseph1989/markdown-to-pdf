"""Pre-processing: GitHub Alerts, Frontmatter, Task Lists, Relative Images."""

import re
from pathlib import Path

ALERT_STYLES = {
    "NOTE": {
        "color": "#0969da",
        "bg": "#f0f7ff",
        "border": "#54aeff",
        "title": "Note",
        "icon": "ℹ️",
    },
    "TIP": {
        "color": "#1a7f37",
        "bg": "#f6fcf8",
        "border": "#4ac26b",
        "title": "Tip",
        "icon": "💡",
    },
    "IMPORTANT": {
        "color": "#8250df",
        "bg": "#fbf8ff",
        "border": "#c297ff",
        "title": "Important",
        "icon": "🟣",
    },
    "WARNING": {
        "color": "#9a6700",
        "bg": "#fffcf2",
        "border": "#e3b341",
        "title": "Warning",
        "icon": "⚠️",
    },
    "CAUTION": {
        "color": "#cf222e",
        "bg": "#fff8f8",
        "border": "#ff8182",
        "title": "Caution",
        "icon": "🛑",
    },
}


def preprocess_markdown(text: str, base_dir: Path) -> str:
    """Preprocess Markdown for frontmatter, GitHub alerts, task lists, and images."""
    lines = text.split("\n")
    processed_lines = []
    in_frontmatter = False
    frontmatter_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Extract YAML Frontmatter
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            i += 1
            continue

        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
                # Format frontmatter as a clean metadata block
                if frontmatter_lines:
                    processed_lines.append('<div class="frontmatter-box">')
                    for fml in frontmatter_lines:
                        if ":" in fml:
                            k, v = fml.split(":", 1)
                            clean_k = k.strip().capitalize()
                            clean_v = v.strip().strip('"').strip("'")
                            processed_lines.append(f'<div class="fm-row"><span class="fm-key">{clean_k}:</span> <span class="fm-val">{clean_v}</span></div>')
                    processed_lines.append("</div>\n")
            else:
                frontmatter_lines.append(line)
            i += 1
            continue

        # Handle GitHub-style Alerts: > [!NOTE], > [!TIP], etc.
        alert_match = re.match(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", line, re.IGNORECASE)
        if alert_match:
            alert_type = alert_match.group(1).upper()
            alert_info = ALERT_STYLES.get(alert_type, ALERT_STYLES["NOTE"])

            alert_body_lines = []
            i += 1
            while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ""):
                body_line = lines[i]
                if body_line.startswith(">"):
                    body_line = body_line[1:].lstrip(" ")
                alert_body_lines.append(body_line)
                i += 1

            body_content = "\n".join(alert_body_lines).strip()
            # Convert body lines if any nested markdown
            alert_html = (
                f'<div class="github-alert alert-{alert_type.lower()}">\n'
                f'  <div class="alert-header" style="color: {alert_info["color"]}">'
                f'<span class="alert-icon">{alert_info["icon"]}</span> <strong>{alert_info["title"]}</strong>'
                f'</div>\n'
                f'  <div class="alert-content">\n\n{body_content}\n\n</div>\n'
                f'</div>\n'
            )
            processed_lines.append(alert_html)
            continue

        line = render_task_checkbox(line)
        line = resolve_image_paths(line, base_dir)

        processed_lines.append(line)
        i += 1

    return "\n".join(processed_lines)


def render_task_checkbox(line: str) -> str:
    """Task list checkboxes: - [ ] or - [x]"""
    task_unchecked = re.match(r"^(\s*[-*+]\s+)\[ \]\s+(.*)$", line)
    if task_unchecked:
        indent_bullet = task_unchecked.group(1)
        rest = task_unchecked.group(2)
        return f'{indent_bullet}<input type="checkbox" disabled class="task-checkbox"> {rest}'

    task_checked = re.match(r"^(\s*[-*+]\s+)\[[xX]\]\s+(.*)$", line)
    if task_checked:
        indent_bullet = task_checked.group(1)
        rest = task_checked.group(2)
        return f'{indent_bullet}<input type="checkbox" checked disabled class="task-checkbox"> {rest}'

    return line


def resolve_image_paths(line: str, base_dir: Path) -> str:
    """Resolve relative image paths to absolute file URIs."""
    def replace_img_src(match):
        alt_text = match.group(1)
        img_path = match.group(2).strip()

        # If remote URL or absolute file, leave as is
        if img_path.startswith(("http://", "https://", "file://", "data:")):
            return match.group(0)

        abs_img_path = (base_dir / img_path).resolve()
        if abs_img_path.exists():
            return f"![{alt_text}](file://{abs_img_path})"
        return match.group(0)

    return re.sub(r"!\[(.*?)\]\((.*?)\)", replace_img_src, line)
