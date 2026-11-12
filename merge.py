"""Append the pages of one PDF to the end of another."""

import os
import tempfile
from pathlib import Path


def require_pypdf() -> None:
    """Fail early, before any rendering, when pypdf is missing."""
    try:
        import pypdf  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "--append needs pypdf. Install it with: python3 -m pip install pypdf"
        ) from None


def append_pdf(target: Path, extra: Path, output: Path) -> int:
    """Write target's pages followed by extra's pages to output.

    output may be the same file as target: the result is written to a temporary
    file first and then moved into place, so target is never left half-written.
    Returns the total page count.
    """
    require_pypdf()
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.append(str(target))
    writer.append(str(extra))

    fd, tmp_name = tempfile.mkstemp(suffix=".pdf", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as fh:
            writer.write(fh)
        os.replace(tmp_name, output)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    finally:
        writer.close()

    return len(writer.pages)
