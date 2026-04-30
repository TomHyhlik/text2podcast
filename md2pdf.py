#!/usr/bin/env python3
"""
md2pdf.py — Convert a Markdown file to PDF using Chrome headless.

Dependencies (all free, no extra pip installs needed):
  - Python markdown library (already in requirements.txt)
  - Google Chrome or Chromium installed on the system

Usage:
  .venv/bin/python md2pdf.py input.md
  .venv/bin/python md2pdf.py input.md -o output.pdf
"""

import argparse
import base64
import html
from html.parser import HTMLParser
import mimetypes
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown

CSS = """
body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 13pt;
    line-height: 1.7;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 40px;
    color: #222;
}
h1, h2, h3, h4, h5, h6 {
    font-family: Arial, Helvetica, sans-serif;
    color: #111;
    margin-top: 1.4em;
    margin-bottom: 0.4em;
}
h1 { font-size: 2em; border-bottom: 2px solid #ccc; padding-bottom: 0.2em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.1em; }
code {
    background: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 0.1em 0.4em;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}
pre {
    background: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1em;
    overflow-x: auto;
}
pre code {
    border: none;
    padding: 0;
    background: none;
}
blockquote {
    border-left: 4px solid #ccc;
    margin: 0;
    padding: 0.5em 1em;
    color: #555;
    background: #fafafa;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ccc;
    padding: 0.5em 0.8em;
    text-align: left;
}
th { background: #f0f0f0; font-weight: bold; }
a { color: #0066cc; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
hr { border: none; border-top: 1px solid #ccc; margin: 2em 0; }
"""

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def find_chrome():
    for name in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium"):
        path = shutil.which(name)
        if path:
            return path
    return None


def image_to_data_uri(image_path):
    mime_type = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def resolve_image_src(src, base_dir):
    if not src:
        return src

    parsed = urlsplit(src)
    if parsed.scheme or src.startswith(("#", "//")):
        return src

    image_path = Path(unquote(parsed.path))
    if not image_path.is_absolute():
        image_path = base_dir / image_path

    if not image_path.is_file():
        print(f"Warning: image not found: {image_path}", file=sys.stderr)
        return src

    try:
        return image_to_data_uri(image_path)
    except OSError as exc:
        print(f"Warning: could not read image {image_path}: {exc}", file=sys.stderr)
        return src


class ImageSourceRewriter(HTMLParser):
    def __init__(self, base_dir):
        super().__init__(convert_charrefs=False)
        self.base_dir = base_dir
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.format_tag(tag, attrs, self_closing=False))

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.format_tag(tag, attrs, self_closing=True))

    def handle_endtag(self, tag):
        self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data):
        self.parts.append(f"<?{data}>")

    def format_tag(self, tag, attrs, self_closing):
        rewritten_attrs = []
        for name, value in attrs:
            if tag.lower() == "img" and name.lower() == "src" and value is not None:
                value = resolve_image_src(value, self.base_dir)
            rewritten_attrs.append((name, value))

        attr_text = "".join(
            f" {name}" if value is None else f' {name}="{html.escape(value, quote=True)}"'
            for name, value in rewritten_attrs
        )
        close = " />" if self_closing else ">"
        return f"<{tag}{attr_text}{close}"

    def html(self):
        return "".join(self.parts)


def embed_local_images(html_content, base_dir):
    rewriter = ImageSourceRewriter(base_dir)
    rewriter.feed(html_content)
    rewriter.close()
    return rewriter.html()


def md_to_html(md_text, base_dir):
    extensions = ["tables", "fenced_code", "footnotes", "toc", "attr_list"]
    body = markdown.markdown(md_text, extensions=extensions)
    body = embed_local_images(body, base_dir)
    return HTML_TEMPLATE.format(css=CSS, body=body)


def html_to_pdf(html_content, output_path, chrome_bin):
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        f.write(html_content)
        tmp_html = f.name

    try:
        result = subprocess.run(
            [
                chrome_bin,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-software-rasterizer",
                f"--print-to-pdf={output_path}",
                "--print-to-pdf-no-header",
                f"file://{tmp_html}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Chrome error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
    finally:
        Path(tmp_html).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Convert a Markdown file to PDF.")
    parser.add_argument("input", help="Input .md file")
    parser.add_argument("-o", "--output", help="Output .pdf path (default: same name as input)")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else input_path.with_suffix(".pdf")

    chrome_bin = find_chrome()
    if not chrome_bin:
        print(
            "Error: Google Chrome or Chromium not found. Install with:\n"
            "  sudo apt install chromium-browser",
            file=sys.stderr,
        )
        sys.exit(1)

    md_text = input_path.read_text(encoding="utf-8")
    html_content = md_to_html(md_text, input_path.parent)
    html_to_pdf(html_content, str(output_path), chrome_bin)

    print(f"PDF written to: {output_path}")


if __name__ == "__main__":
    main()
