# text2podcast

A collection of CLI tools for converting Markdown, plain-text, PDF, EPUB documents, and web URLs into audio and PDF outputs.

---

## What it can do

### `text2podcast.py` — document or web page to spoken-word MP3

- **Convert Markdown (`.md`) files to MP3** — parses Markdown to clean plain text, then speaks it
- **Convert plain-text (`.txt`) files to MP3** — reads the file as-is and converts it to audio
- **Convert PDF (`.pdf`) files to MP3** — extracts text from each page and converts it to audio
- **Convert EPUB (`.epub`) files to MP3** — extracts text from all chapters and converts to audio
- **Convert web URLs to MP3** — fetches any `http`/`https` URL and extracts the readable content; HTML pages use `trafilatura` to strip ads/nav and isolate the article; raw `.md` and `.txt` URLs are fetched and processed directly; output filename is derived from the URL slug
- **High-quality neural voices (online)** — uses Microsoft Edge TTS (`edge-tts`) with ~400 voices across many languages; no API key required
- **Offline fallback** — uses `espeak-ng` + `lame` when no internet is available; lower quality but fully local
- **Choose any voice** — pass `--voice en-GB-SoniaNeural` (or any other) to pick a specific voice
- **List all available voices** — run `--list-voices` to print the full list (~400 voices)
- **Custom output path** — default is the same filename as input with `.mp3` extension; override with `-o`

### `md2pdf.py` — Markdown to styled PDF

- **Convert Markdown (`.md`) files to PDF** — renders to a clean, readable document
- **No extra pip packages** — only requires the Python `markdown` library (already in `requirements.txt`) and Chrome/Chromium
- **Styled output** — serif body font, code blocks with syntax highlighting background, tables, blockquotes, and headings with borders
- **Full Markdown feature support** — tables, fenced code blocks, footnotes, table of contents, and attribute lists
- **Custom output path** — default is the same filename as input with `.pdf` extension; override with `-o`
- **Auto-detects Chrome or Chromium** — works with `google-chrome`, `google-chrome-stable`, `chromium-browser`, or `chromium`

---

## How it works

**text2podcast.py:**
```
.md / .txt / .pdf / .epub / http(s) URL  →  plain text  →  TTS engine  →  .mp3
```

| Step | Tool | Purpose |
|------|------|---------|
| Markdown → HTML | Python `markdown` library | Parse and render `.md` |
| HTML → plain text | `beautifulsoup4` | Strip tags, produce readable text |
| Plain text | _(read directly)_ | `.txt` files are used as-is |
| PDF → plain text | `pymupdf` | Extract text from `.pdf` files |
| EPUB → plain text | `ebooklib` + `beautifulsoup4` | Extract chapter text from `.epub` files |
| HTML page → plain text | `trafilatura` | Fetch URL, strip boilerplate, extract article text |
| Raw `.md`/`.txt` URL | `urllib` + `markdown` | Fetch and process remote Markdown or plain-text files |
| Text → MP3 (online) | `edge-tts` | Microsoft Edge TTS, free, high-quality neural voices |
| Text → WAV (offline) | `espeak-ng` | System TTS, no internet required |
| WAV → MP3 (offline) | `lame` | Encode WAV to MP3 when using espeak-ng |

**md2pdf.py:**
```
.md  →  Python markdown  →  styled HTML  →  Chrome headless  →  .pdf
```

---

## System requirements

| Package | Install command | Purpose |
|---------|----------------|---------|
| Python 3.x | pre-installed on Ubuntu | Runtime |
| `espeak-ng` | `sudo apt install espeak-ng` | Offline TTS fallback |
| `lame` | `sudo apt install lame` | MP3 encoder for offline fallback |
| Google Chrome / Chromium | `sudo apt install chromium-browser` | PDF rendering (`md2pdf.py`) |

---

## Setup

```bash
# Install system packages
sudo apt install espeak-ng lame chromium-browser

# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## Usage

### `text2podcast.py`

```bash
# Basic — output MP3 next to input file (online, neural voice)
.venv/bin/python text2podcast.py your_file.md
.venv/bin/python text2podcast.py your_file.txt
.venv/bin/python text2podcast.py your_file.pdf
.venv/bin/python text2podcast.py your_file.epub

# Convert a web page URL (output named after URL slug)
.venv/bin/python text2podcast.py https://example.com/some-article
.venv/bin/python text2podcast.py https://raw.githubusercontent.com/.../notes.md

# Specify output path
.venv/bin/python text2podcast.py your_file.md -o output/episode1.mp3
.venv/bin/python text2podcast.py https://example.com/article -o episode1.mp3

# Choose a different voice
.venv/bin/python text2podcast.py your_file.md --voice en-GB-SoniaNeural

# List all available voices (~400)
.venv/bin/python text2podcast.py --list-voices

# Offline mode (no internet required, lower quality)
.venv/bin/python text2podcast.py your_file.md --offline
```

### `md2pdf.py`

```bash
# Basic — output PDF next to input file
.venv/bin/python md2pdf.py your_file.md

# Specify output path
.venv/bin/python md2pdf.py your_file.md -o /path/to/output.pdf
```

---

## Agent workflows

These workflows are for coding agents operating from this repository.

### "make podcast"

When the user asks to **"make podcast"** or uses similar wording such as "convert to podcast", "make mp3", or "podcast this":

1. Identify the input from the user's message. It can be a local `.md`, `.txt`, `.pdf`, or `.epub` file, or an `http`/`https` URL.
2. Convert it to MP3:

   ```bash
   /home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py <file_or_url>
   ```

   For local files, the MP3 is created next to the input file with the same name and an `.mp3` extension. For URLs, the MP3 is saved in the current working directory and named after the URL slug.

3. Send the MP3 via Telegram:

   ```bash
   /home/fuzz/Repos/sender-tool/telegram/send-file.sh --file <output.mp3> --caption "<filename>"
   ```

Do these steps automatically without asking for confirmation.

### "send it"

When the user says **"send it"** after a podcast has been created, send the most recently generated MP3:

```bash
/home/fuzz/Repos/sender-tool/telegram/send-file.sh --file <last_mp3>
```

Telegram config is pre-configured at `/home/fuzz/Repos/sender-tool/telegram/config.json`; no credentials are needed.

---

## Project structure

```
text2podcast/
├── .venv/                  # Python virtual environment (not committed)
├── AGENTS.md               # Agent instructions pointer
├── CLAUDE.md               # Claude instructions pointer
├── text2podcast.py         # Document/URL → MP3 conversion
├── md2pdf.py               # MD → PDF conversion
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Tested on

- Ubuntu 24.04 LTS
- Python 3.12.3
- edge-tts 7.2.8

---

## Default voice

`en-US-AriaNeural` — American English, female, natural neural voice.

Run `--list-voices` to see all ~400 available voices across many languages.
