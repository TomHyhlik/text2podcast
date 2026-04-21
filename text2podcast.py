#!/usr/bin/env python3
"""
text2podcast — Convert a Markdown, plain-text, or PDF file to an MP3 spoken-word file.

Primary TTS: edge-tts  (Microsoft Edge TTS, free, requires internet)
Fallback TTS: espeak-ng (offline, installed system-wide)
"""

import argparse
import asyncio
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


def md_to_plaintext(md_path: Path) -> str:
    """Convert Markdown file to clean plain text."""
    raw = md_path.read_text(encoding="utf-8")

    # Render to HTML then strip tags for clean, readable text
    html = markdown.markdown(raw, extensions=["extra", "sane_lists"])
    soup = BeautifulSoup(html, "html.parser")

    # Replace block-level elements with line breaks so sentences flow naturally
    for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6"]):
        tag.insert_before("\n")
        tag.insert_after("\n")

    text = soup.get_text()

    # Collapse excess whitespace / blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def epub_to_plaintext(epub_path: Path) -> str:
    """Extract plain text from an EPUB file using ebooklib and BeautifulSoup."""
    import ebooklib
    from ebooklib import epub

    book = epub.read_epub(str(epub_path), options={"ignore_ncx": True})
    parts = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6"]):
            tag.insert_before("\n")
            tag.insert_after("\n")
        parts.append(soup.get_text())

    text = "\n\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def pdf_to_plaintext(pdf_path: Path) -> str:
    """Extract plain text from a PDF file using pymupdf."""
    import fitz  # pymupdf

    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()

    text = "\n\n".join(pages)
    # Collapse excess whitespace / blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


async def tts_edge(text: str, output_mp3: Path, voice: str) -> None:
    """Convert text to MP3 using edge-tts."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_mp3))


def tts_espeak(text: str, output_mp3: Path) -> None:
    """Convert text to MP3 using espeak-ng + lame (offline fallback)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    subprocess.run(
        ["espeak-ng", "-w", wav_path, text],
        check=True,
    )
    subprocess.run(
        ["lame", wav_path, str(output_mp3)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    Path(wav_path).unlink(missing_ok=True)


def convert(input_path: Path, output_mp3: Path, voice: str, offline: bool) -> None:
    print(f"Reading: {input_path}")
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        text = pdf_to_plaintext(input_path)
    elif suffix == ".epub":
        text = epub_to_plaintext(input_path)
    elif suffix == ".txt":
        text = input_path.read_text(encoding="utf-8").strip()
    else:
        text = md_to_plaintext(input_path)
    print(f"Text length: {len(text)} characters")

    if offline:
        print("TTS engine: espeak-ng (offline)")
        tts_espeak(text, output_mp3)
    else:
        print(f"TTS engine: edge-tts  voice={voice}")
        asyncio.run(tts_edge(text, output_mp3, voice))

    print(f"Output: {output_mp3}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Markdown, plain-text, PDF, or EPUB file to a spoken-word MP3."
    )
    parser.add_argument("input", type=Path, help="Path to the .md, .txt, .pdf, or .epub file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output MP3 path (default: same name as input with .mp3 extension)",
    )
    parser.add_argument(
        "--voice",
        default="en-US-AriaNeural",
        help="edge-tts voice name (default: en-US-AriaNeural). "
        "Run `edge-tts --list-voices` to see all options.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use espeak-ng instead of edge-tts (no internet required, lower quality)",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available edge-tts voices and exit",
    )

    args = parser.parse_args()

    if args.list_voices:
        subprocess.run([sys.executable, "-m", "edge_tts", "--list-voices"])
        return

    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.input.suffix.lower() not in (".md", ".pdf", ".txt", ".epub"):
        print(f"Error: unsupported file type '{args.input.suffix}' — use .md, .txt, .pdf, or .epub", file=sys.stderr)
        sys.exit(1)

    output = args.output or args.input.with_suffix(".mp3")
    convert(args.input, output, args.voice, args.offline)


if __name__ == "__main__":
    main()
