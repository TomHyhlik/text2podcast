# text2podcast

Convert any Markdown (`.md`) file into a spoken-word MP3 file using free tools.

---

## How it works

```
.md file  →  plain text (pandoc / BeautifulSoup)  →  TTS engine  →  .mp3
```

| Step | Tool | Purpose |
|------|------|---------|
| Markdown → HTML | Python `markdown` library | Parse and render `.md` |
| HTML → plain text | `beautifulsoup4` | Strip tags, produce readable text |
| Text → MP3 (online) | `edge-tts` | Microsoft Edge TTS, free, high-quality neural voices |
| Text → WAV (offline) | `espeak-ng` | System TTS, no internet required |
| WAV → MP3 (offline) | `lame` | Encode WAV to MP3 when using espeak-ng |

---

## System requirements

| Package | Install command | Purpose |
|---------|----------------|---------|
| Python 3.x | pre-installed on Ubuntu | Runtime |
| `espeak-ng` | `sudo apt install espeak-ng` | Offline TTS fallback |
| `lame` | `sudo apt install lame` | MP3 encoder for offline fallback |
| `ffmpeg` | `sudo apt install ffmpeg` | General audio processing (available for future use) |

> **Note:** `pandoc` was evaluated but is not required — Markdown is parsed
> entirely via the Python `markdown` + `beautifulsoup4` stack.

---

## Setup

### 1. Install system packages

```bash
sudo apt install espeak-ng lame ffmpeg
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Basic (online, high-quality neural voice)

```bash
.venv/bin/python text2podcast.py your_file.md
```

Produces `your_file.mp3` in the same directory.

### Specify output path

```bash
.venv/bin/python text2podcast.py your_file.md -o output/episode1.mp3
```

### Choose a different voice

```bash
.venv/bin/python text2podcast.py your_file.md --voice en-GB-SoniaNeural
```

### List all available voices

```bash
.venv/bin/python text2podcast.py --list-voices
```

### Offline mode (no internet required)

Uses `espeak-ng` for TTS and `lame` to encode to MP3. Lower quality but fully local.

```bash
.venv/bin/python text2podcast.py your_file.md --offline
```

---

## Python packages installed (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `edge-tts` | 7.2.8 | Microsoft Edge TTS client |
| `markdown` | 3.10.2 | Markdown → HTML parser |
| `beautifulsoup4` | 4.14.3 | HTML → plain text extraction |
| `aiohttp` | 3.13.4 | Async HTTP (dependency of edge-tts) |
| `aiohappyeyeballs` | 2.6.1 | Async DNS (dependency of aiohttp) |
| `aiosignal` | 1.4.0 | Async signal handling |
| `attrs` | 26.1.0 | Data classes utility |
| `certifi` | 2026.2.25 | TLS certificates |
| `frozenlist` | 1.8.0 | Immutable list type |
| `idna` | 3.11 | Internationalized domain names |
| `multidict` | 6.7.1 | Multi-value dict (aiohttp) |
| `propcache` | 0.4.1 | Property caching (aiohttp) |
| `soupsieve` | 2.8.3 | CSS selector engine (bs4) |
| `tabulate` | 0.10.0 | Table formatting (edge-tts CLI) |
| `typing_extensions` | 4.15.0 | Backported typing hints |
| `yarl` | 1.23.0 | URL parsing (aiohttp) |

---

---

## Markdown to PDF (`md2pdf.py`)

Convert any `.md` file to a styled PDF using Chrome headless — no extra pip packages required beyond what's already in `requirements.txt`.

### System requirements

| Package | Install command | Purpose |
|---------|----------------|---------|
| Google Chrome | `sudo apt install google-chrome-stable` | Headless PDF renderer |
| *(or Chromium)* | `sudo apt install chromium-browser` | Alternative renderer |

> Chrome/Chromium is the only additional system dependency. The Python `markdown` library is already in `requirements.txt`.

### Usage

**Basic — output PDF next to input file:**

```bash
.venv/bin/python md2pdf.py your_file.md
```

Produces `your_file.pdf` in the same directory.

**Specify output path:**

```bash
.venv/bin/python md2pdf.py your_file.md -o /path/to/output.pdf
```

### How it works

```
.md file  →  Python markdown library  →  styled HTML  →  Chrome headless  →  .pdf
```

1. Parses Markdown to HTML (supports tables, fenced code blocks, footnotes, TOC)
2. Wraps the HTML with a clean CSS stylesheet (serif body font, code blocks, tables)
3. Calls Chrome `--headless=new --print-to-pdf` on a temporary HTML file

---

## Project structure

```
text2podcast/
├── .venv/                  # Python virtual environment (not committed)
├── text2podcast.py         # Main conversion script (MD → MP3)
├── md2pdf.py               # MD → PDF conversion script
├── sample.md               # Example input file
├── sample.mp3              # Example output (generated)
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
