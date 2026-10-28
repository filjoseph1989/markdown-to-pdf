"""Command-line interface: parse arguments and convert a file or a whole directory."""

import argparse
import sys
from pathlib import Path

from .converter import render_markdown_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md_to_pdf",
        description="Convert Markdown (.md) documents to clean, beautifully formatted PDFs.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the markdown file (or directory of markdown files)",
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
    return parser


def convert_file(args: argparse.Namespace, input_path: Path) -> None:
    try:
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
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


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
        except Exception as err:
            print(f"  ✗ Failed to convert {f.name}: {err}", file=sys.stderr)

    print(f"\nCompleted: {success_count}/{len(md_files)} files converted.")


def main() -> None:
    args = build_parser().parse_args()
    input_path = args.input.resolve()

    if input_path.is_file():
        convert_file(args, input_path)
    elif input_path.is_dir():
        convert_directory(args, input_path)
    else:
        print(f"Error: Specified path '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)
