#!/usr/bin/env python3
"""
text2podcast — Convert a Markdown, plain-text, PDF, EPUB file or web URL to an MP3 spoken-word file.

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


def _reddit_to_plaintext(url: str) -> str:
    """Extract post + top comments from a Reddit thread via the public JSON API."""
    import json
    import urllib.request

    api_url = url.rstrip("/") + ".json?limit=50&raw_json=1"
    req = urllib.request.Request(api_url, headers={"User-Agent": "text2podcast/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    post = data[0]["data"]["children"][0]["data"]
    title = post.get("title", "")
    selftext = post.get("selftext", "").strip()

    parts = [title]
    if selftext:
        parts.append(selftext)

    comments_listing = data[1]["data"]["children"]
    for child in comments_listing:
        if child.get("kind") != "t1":
            continue
        body = child["data"].get("body", "").strip()
        if body and body != "[deleted]" and body != "[removed]":
            parts.append(body)

    text = "\n\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def url_to_plaintext(url: str) -> str:
    """Fetch a web page or raw file and extract its main readable text content."""
    import urllib.request

    from urllib.parse import urlparse

    url_path = urlparse(url).path.lower()

    # Raw text/markdown files: fetch and process directly
    if url_path.endswith(".md"):
        with urllib.request.urlopen(url) as resp:
            raw = resp.read().decode("utf-8")
        html = markdown.markdown(raw, extensions=["extra", "sane_lists"])
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6"]):
            tag.insert_before("\n")
            tag.insert_after("\n")
        text = soup.get_text()
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    if url_path.endswith(".txt"):
        with urllib.request.urlopen(url) as resp:
            return resp.read().decode("utf-8").strip()

    # Reddit posts: use the public JSON API
    parsed = urlparse(url)
    if parsed.netloc in ("www.reddit.com", "reddit.com", "old.reddit.com"):
        return _reddit_to_plaintext(url)

    # HTML pages: use trafilatura to extract main article content
    import trafilatura

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        # Fallback: fetch with a browser User-Agent
        req = urllib.request.Request(url, headers=_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                downloaded = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise ValueError(f"Failed to fetch URL: {url}") from exc

    text = trafilatura.extract(downloaded)
    if not text:
        raise ValueError(f"Could not extract readable content from: {url}")

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


def convert(input_path: Path | None, output_mp3: Path, voice: str, offline: bool, url: str | None = None) -> None:
    if url is not None:
        print(f"Fetching: {url}")
        text = url_to_plaintext(url)
    else:
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


def _slug_from_url(url: str) -> str:
    """Derive a safe filename stem from a URL."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    last_segment = parsed.path.rstrip("/").rsplit("/", 1)[-1]
    stem = Path(last_segment).stem if last_segment else ""
    slug = re.sub(r"[^\w-]", "_", stem)[:80] if stem else ""
    return slug or re.sub(r"[^\w-]", "_", parsed.netloc) or "webpage"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Markdown, plain-text, PDF, EPUB file or web URL to a spoken-word MP3."
    )
    parser.add_argument(
        "input",
        help="Path to a .md, .txt, .pdf, or .epub file — or an http/https URL",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output MP3 path (default: derived from input name/URL)",
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

    input_str: str = args.input
    is_url = input_str.startswith("http://") or input_str.startswith("https://")

    if is_url:
        output = args.output or Path(_slug_from_url(input_str) + ".mp3")
        convert(None, output, args.voice, args.offline, url=input_str)
    else:
        input_path = Path(input_str)
        if not input_path.exists():
            print(f"Error: file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        if input_path.suffix.lower() not in (".md", ".pdf", ".txt", ".epub"):
            print(f"Error: unsupported file type '{input_path.suffix}' — use .md, .txt, .pdf, or .epub", file=sys.stderr)
            sys.exit(1)
        output = args.output or input_path.with_suffix(".mp3")
        convert(input_path, output, args.voice, args.offline)


if __name__ == "__main__":
    main()
