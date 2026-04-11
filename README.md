# text2podcast

A collection of CLI tools for converting Markdown, plain-text, and PDF documents into audio and PDF outputs.

---

## What it can do

### `text2podcast.py` — document to spoken-word MP3

- **Convert Markdown (`.md`) files to MP3** — parses Markdown to clean plain text, then speaks it
- **Convert plain-text (`.txt`) files to MP3** — reads the file as-is and converts it to audio
- **Convert PDF (`.pdf`) files to MP3** — extracts text from each page and converts it to audio
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
.md / .txt / .pdf  →  plain text  →  TTS engine  →  .mp3
```

| Step | Tool | Purpose |
|------|------|---------|
| Markdown → HTML | Python `markdown` library | Parse and render `.md` |
| HTML → plain text | `beautifulsoup4` | Strip tags, produce readable text |
| Plain text | _(read directly)_ | `.txt` files are used as-is |
| PDF → plain text | `pymupdf` | Extract text from `.pdf` files |
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

# Specify output path
.venv/bin/python text2podcast.py your_file.md -o output/episode1.mp3

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

## Project structure

```
text2podcast/
├── .venv/                  # Python virtual environment (not committed)
├── text2podcast.py         # MD/PDF → MP3 conversion
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
