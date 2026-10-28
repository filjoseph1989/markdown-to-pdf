"""Browser / renderer detection and HTML-to-PDF printing."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_chromium_executable() -> Optional[str]:
    """Find available Chromium-based browser (Chrome, Brave, Edge, Chromium)."""
    # macOS application bundle locations
    mac_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        os.path.expanduser("~/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        os.path.expanduser("~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]

    for p in mac_paths:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p

    # System PATH binaries (Linux, macOS with homebrew, Windows)
    binary_names = [
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
        "brave-browser",
        "brave",
        "microsoft-edge",
        "msedge",
    ]

    for b in binary_names:
        found = shutil.which(b)
        if found:
            return found

    return None


def generate_pdf_with_chromium(
    html_path: Path,
    output_pdf: Path,
    browser_bin: str,
    landscape: bool = False,
) -> bool:
    """Render HTML to PDF using a Chromium-based browser."""
    cmd = [
        browser_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        # Give KaTeX time to load from the CDN and render before printing
        "--virtual-time-budget=10000",
        f"--print-to-pdf={output_pdf}",
    ]

    if landscape:
        cmd.append("--print-to-pdf-orientation=landscape")

    cmd.append(f"file://{html_path.resolve()}")

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if output_pdf.exists() and output_pdf.stat().st_size > 0:
            return True
        if res.returncode != 0:
            print(f"Renderer error: {res.stderr}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Error: Rendering timed out after 60 seconds.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error executing browser: {e}", file=sys.stderr)
        return False

    return output_pdf.exists() and output_pdf.stat().st_size > 0


def generate_pdf_with_weasyprint(html_path: Path, output_pdf: Path) -> bool:
    """Render HTML to PDF using WeasyPrint if available."""
    try:
        res = subprocess.run(["weasyprint", str(html_path), str(output_pdf)], capture_output=True, text=True)
        return res.returncode == 0 and output_pdf.exists()
    except FileNotFoundError:
        return False


def generate_pdf_with_wkhtmltopdf(html_path: Path, output_pdf: Path) -> bool:
    """Render HTML to PDF using wkhtmltopdf if available."""
    try:
        res = subprocess.run(["wkhtmltopdf", str(html_path), str(output_pdf)], capture_output=True, text=True)
        return res.returncode == 0 and output_pdf.exists()
    except FileNotFoundError:
        return False
