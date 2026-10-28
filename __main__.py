"""Entry point for `python3 md_to_pdf <file.md>` and `python3 -m md_to_pdf <file.md>`."""

import sys
from pathlib import Path

if not __package__:
    # Run as `python3 md_to_pdf`: Python put this folder on the path, so swap it for the
    # parent folder; the package then resolves and its modules can't shadow real libraries
    sys.path[0] = str(Path(__file__).resolve().parent.parent)

from md_to_pdf.cli import main

main()
