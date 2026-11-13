"""Join PDFs: append one to another, or combine several into one."""

import os
import tempfile
from pathlib import Path
from typing import List


def require_pypdf() -> None:
    """Fail early, before any rendering, when pypdf is missing."""
    try:
        import pypdf  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "--append and --combine need pypdf. Install it with: python3 -m pip install pypdf"
        ) from None


def append_pdf(target: Path, extra: Path, output: Path) -> int:
    """Write target's pages followed by extra's pages to output."""
    return merge_pdfs([target, extra], output)


def merge_pdfs(sources: List[Path], output: Path) -> int:
    """Write the pages of every PDF in sources, in order, to output.

    output may be one of the sources: the result is written to a temporary
    file first and then moved into place, so no file is left half-written.
    Returns the total page count.
    """
    require_pypdf()
    from pypdf import PdfWriter

    writer = PdfWriter()
    for source in sources:
        writer.append(str(source))

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
