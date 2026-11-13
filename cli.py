"""Command-line interface: convert a file or a whole directory, or append/combine into one PDF."""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

from .converter import render_markdown_file
from .merge import append_pdf, merge_pdfs, require_pypdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md_to_pdf",
        description="Convert Markdown (.md) documents to clean, beautifully formatted PDFs.",
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="+",
        help="Path to the markdown file (or directory of markdown files). "
             "With --combine: any number of Markdown files, PDFs and directories",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Path for output PDF file (defaults to same name with .pdf extension)",
    )
    parser.add_argument(
        "--page-size",
        choices=["A4", "Letter", "Legal"],
        default="A4",
        help="Page format size (default: A4)",
    )
    parser.add_argument(
        "--margin",
        default="18mm",
        help="CSS page margin, e.g. '20mm' or '15mm' (default: '18mm')",
    )
    parser.add_argument(
        "--landscape",
        action="store_true",
        help="Render in landscape orientation",
    )
    parser.add_argument(
        "--browser",
        type=str,
        default=None,
        help="Custom path to Chromium/Chrome/Brave/Edge executable",
    )
    parser.add_argument(
        "--keep-html",
        action="store_true",
        help="Keep the generated intermediate HTML file for debugging",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated PDF automatically after conversion (macOS)",
    )
    parser.add_argument(
        "--delete-md",
        action="store_true",
        help="Delete the source Markdown file after it is successfully converted",
    )
    parser.add_argument(
        "--append",
        type=Path,
        default=None,
        metavar="PDF",
        help="Add the converted Markdown as new pages at the end of an existing PDF "
             "(written back to that PDF, or to -o if given). Requires pypdf.",
    )
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Join all inputs, in the order given, into the single PDF named by -o. "
             "Markdown files are converted first, PDFs are used as they are, and a "
             "directory adds its .md files in name order. Requires pypdf.",
    )
    return parser


def convert_file(args: argparse.Namespace, input_path: Path) -> None:
    try:
        if args.append:
            out = append_file(args, input_path)
        else:
            out = render_markdown_file(
                input_file=input_path,
                output_pdf=args.output,
                page_size=args.page_size,
                margin=args.margin,
                landscape=args.landscape,
                custom_browser=args.browser,
                keep_html=args.keep_html,
                open_after=args.open,
            )
            print(f"✓ Successfully generated PDF: {out}")
        if args.delete_md:
            input_path.unlink()
            print(f"✓ Deleted source Markdown: {input_path}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def append_file(args: argparse.Namespace, input_path: Path) -> Path:
    """Render input_path and add its pages to the end of args.append."""
    target = args.append.resolve()
    output = (args.output or args.append).resolve()
    render_options = dict(
        page_size=args.page_size,
        margin=args.margin,
        landscape=args.landscape,
        custom_browser=args.browser,
        keep_html=args.keep_html,
    )

    if not target.exists():
        # Nothing to append to yet: start the PDF with this document.
        render_markdown_file(input_file=input_path, output_pdf=output, **render_options)
        print(f"✓ {target.name} did not exist; created {output}")
    else:
        if not target.is_file():
            raise ValueError(f"--append target is not a file: {target}")
        require_pypdf()
        fd, tmp_name = tempfile.mkstemp(suffix=".pdf", dir=output.parent)
        os.close(fd)
        new_pages = Path(tmp_name)
        try:
            render_markdown_file(input_file=input_path, output_pdf=new_pages, **render_options)
            total = append_pdf(target, new_pages, output)
        finally:
            new_pages.unlink(missing_ok=True)
        print(f"✓ Appended {input_path.name} to {target.name}: {output} ({total} pages)")

    if args.open and sys.platform == "darwin":
        subprocess.run(["open", str(output)])
    return output


def convert_directory(args: argparse.Namespace, input_path: Path) -> None:
    md_files = list(input_path.glob("*.md"))
    if not md_files:
        print(f"No Markdown (.md) files found in directory: {input_path}")
        sys.exit(0)

    out_dir = args.output if args.output and args.output.is_dir() else input_path
    print(f"Converting {len(md_files)} Markdown files in {input_path}...")

    success_count = 0
    for f in sorted(md_files):
        try:
            dest_pdf = (out_dir / f.name).with_suffix(".pdf")
            render_markdown_file(
                input_file=f,
                output_pdf=dest_pdf,
                page_size=args.page_size,
                margin=args.margin,
                landscape=args.landscape,
                custom_browser=args.browser,
                keep_html=args.keep_html,
                open_after=False,
            )
            print(f"  ✓ {f.name} -> {dest_pdf.name}")
            success_count += 1
            if args.delete_md:
                f.unlink()
                print(f"    deleted {f.name}")
        except Exception as err:
            print(f"  ✗ Failed to convert {f.name}: {err}", file=sys.stderr)

    print(f"\nCompleted: {success_count}/{len(md_files)} files converted.")


def collect_combine_sources(inputs: List[Path]) -> List[Path]:
    """Expand the inputs into an ordered list of Markdown and PDF files."""
    sources: List[Path] = []
    for raw in inputs:
        path = raw.resolve()
        if path.is_dir():
            md_files = sorted(path.glob("*.md"))
            if not md_files:
                print(f"  (no .md files in {raw}, skipped)")
            sources.extend(md_files)
        elif path.is_file():
            sources.append(path)
        else:
            raise FileNotFoundError(f"Input not found: {raw}")
    if not sources:
        raise ValueError("Nothing to combine: no Markdown or PDF files found in the inputs.")
    return sources


def combine_inputs(args: argparse.Namespace) -> None:
    """Convert the Markdown inputs and join everything into one PDF."""
    try:
        if args.output is None:
            raise ValueError("--combine needs -o/--output for the combined PDF.")
        if args.append:
            raise ValueError("--combine can't be used with --append; list the PDF as an input instead.")
        output = args.output.resolve()
        if output.is_dir():
            raise ValueError(f"-o must be a PDF file path, not a directory: {args.output}")
        require_pypdf()

        sources = collect_combine_sources(args.input)
        markdown = [s for s in sources if s.suffix.lower() != ".pdf"]
        print(f"Combining {len(sources)} files into {output.name}...")

        with tempfile.TemporaryDirectory() as tmp:
            pdfs: List[Path] = []
            for i, source in enumerate(sources):
                if source.suffix.lower() == ".pdf":
                    pdfs.append(source)
                    print(f"  + {source.name}")
                    continue
                rendered = Path(tmp) / f"{i:04d}_{source.stem}.pdf"
                render_markdown_file(
                    input_file=source,
                    output_pdf=rendered,
                    page_size=args.page_size,
                    margin=args.margin,
                    landscape=args.landscape,
                    custom_browser=args.browser,
                    keep_html=args.keep_html,
                )
                pdfs.append(rendered)
                print(f"  ✓ {source.name}")
            total = merge_pdfs(pdfs, output)

        print(f"✓ Combined {len(sources)} files into {output} ({total} pages)")
        if args.delete_md:
            for md in markdown:
                md.unlink()
                print(f"  deleted {md.name}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.open and sys.platform == "darwin":
        subprocess.run(["open", str(output)])


def main() -> None:
    args = build_parser().parse_args()

    if args.combine:
        combine_inputs(args)
        return
    if len(args.input) > 1:
        print("Error: several inputs need --combine (and -o for the combined PDF).", file=sys.stderr)
        sys.exit(1)

    args.input = args.input[0]
    input_path = args.input.resolve()

    if input_path.is_file():
        convert_file(args, input_path)
    elif input_path.is_dir() and args.append:
        print("Error: --append works with a single Markdown file, not a directory.", file=sys.stderr)
        sys.exit(1)
    elif input_path.is_dir():
        convert_directory(args, input_path)
    else:
        print(f"Error: Specified path '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)
