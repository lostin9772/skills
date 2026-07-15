#!/usr/bin/env python3
"""Pack a local HTML document and local resources into a single MHTML file."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
import sys
from email.utils import formatdate, make_msgid
from pathlib import Path
from urllib.parse import unquote, urlparse


ATTR_REF_RE = re.compile(
    r"""(?P<attr>\b(?:src|href)\s*=\s*)(?P<quote>["'])(?P<url>.*?)(?P=quote)""",
    re.IGNORECASE | re.DOTALL,
)


def is_packable_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme and parsed.scheme.lower() not in {"file"}:
        return False
    if url.startswith(("#", "data:", "mailto:", "javascript:")):
        return False
    return bool(url.strip())


def resolve_resource(url: str, root: Path, html_dir: Path) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme.lower() == "file":
        candidate = Path(unquote(parsed.path))
    else:
        clean = unquote(parsed.path)
        candidate = (html_dir / clean).resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        return None

    if candidate.is_file():
        return candidate
    return None


def content_type_for(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed:
        if guessed.startswith("text/") or guessed in {"image/svg+xml", "application/javascript"}:
            return f"{guessed}; charset=utf-8"
        return guessed
    return "application/octet-stream"


def encode_part(path: Path) -> str:
    data = path.read_bytes()
    encoded = base64.encodebytes(data).decode("ascii")
    return encoded.replace("\n", "\r\n")


def html_references(html: str, root: Path, html_dir: Path) -> list[tuple[str, Path]]:
    resources: dict[str, Path] = {}
    for match in ATTR_REF_RE.finditer(html):
        url = match.group("url").strip()
        if not is_packable_url(url):
            continue
        path = resolve_resource(url, root, html_dir)
        if path is not None:
            resources.setdefault(url, path)
    return list(resources.items())


def build_mhtml(input_html: Path, output_mhtml: Path, root: Path) -> None:
    html = input_html.read_text(encoding="utf-8")
    html_dir = input_html.parent.resolve()
    refs = html_references(html, root, html_dir)
    boundary = "----=_NextPart_" + make_msgid(domain="source-reading-map.local").strip("<>")

    lines: list[str] = [
        "From: <Saved by Source Reading Map>",
        "Subject: Source Reading Map",
        f"Date: {formatdate(localtime=True)}",
        "MIME-Version: 1.0",
        f'Content-Type: multipart/related; type="text/html"; boundary="{boundary}"',
        "",
        "This is a multi-part message in MIME format.",
        "",
        f"--{boundary}",
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: base64",
        f"Content-Location: {input_html.name}",
        "",
        base64.encodebytes(html.encode("utf-8")).decode("ascii").replace("\n", "\r\n"),
        "",
    ]

    for original_url, path in refs:
        lines.extend(
            [
                f"--{boundary}",
                f"Content-Type: {content_type_for(path)}",
                "Content-Transfer-Encoding: base64",
                f"Content-Location: {original_url}",
                "",
                encode_part(path),
                "",
            ]
        )

    lines.append(f"--{boundary}--")
    lines.append("")
    output_mhtml.write_text("\r\n".join(lines), encoding="utf-8", newline="")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pack a local HTML file and referenced local src/href resources into a single .mhtml file."
    )
    parser.add_argument("input_html", type=Path, help="Path to the source HTML file.")
    parser.add_argument("output_mhtml", type=Path, help="Path to write the .mhtml file.")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Resource root. Defaults to the input HTML directory. References outside this root are skipped.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_html = args.input_html.resolve()
    output_mhtml = args.output_mhtml.resolve()
    root = (args.root.resolve() if args.root else input_html.parent.resolve())

    if not input_html.is_file():
        print(f"Input HTML does not exist: {input_html}", file=sys.stderr)
        return 2
    if input_html.suffix.lower() not in {".html", ".htm"}:
        print(f"Input should be an HTML file: {input_html}", file=sys.stderr)
        return 2

    output_mhtml.parent.mkdir(parents=True, exist_ok=True)
    build_mhtml(input_html, output_mhtml, root)
    print(f"Wrote {output_mhtml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
