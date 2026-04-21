---
name: text2podcast
description: Converts Markdown, plain-text, PDF, or EPUB files to MP3 audio, or converts Markdown to a styled PDF. Use this agent when the user wants to make a podcast, convert a document to audio or PDF, or list available TTS voices. Does NOT handle sending — use the send-file agent for that.
---

# text2podcast

Convert Markdown, plain-text, PDF, or EPUB files to MP3 audio, or convert Markdown to a styled PDF.

## Tool paths

```
PYTHON = /home/fuzz/Repos/text2podcast/.venv/bin/python
SCRIPT = /home/fuzz/Repos/text2podcast/text2podcast.py
MD2PDF = /home/fuzz/Repos/text2podcast/md2pdf.py
```

## Convert Markdown, plain-text, or PDF to MP3 (online, neural voice)

Default voice: `en-US-AriaNeural`. Output is placed next to the input file.

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py <file.md|file.txt|file.pdf|file.epub>
```

## Convert to MP3 with a custom output path

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py <file.md> -o <output.mp3>
```

## Convert to MP3 with a specific voice

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py <file.md> --voice en-GB-SoniaNeural
```

## List all available voices (~400 across many languages)

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py --list-voices
```

## Convert to MP3 offline (no internet, espeak-ng + lame, lower quality)

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py <file.md> --offline
```

## Convert Markdown to styled PDF (requires Chrome/Chromium)

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/md2pdf.py <file.md>
```

## Convert Markdown to PDF with a custom output path

```bash
/home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/md2pdf.py <file.md> -o <output.pdf>
```

## Notes

- Output is placed next to the input file by default (same name, different extension)
- MP3 conversion supports `.md`, `.txt`, `.pdf`, and `.epub` input
- PDF conversion supports `.md` input only
- To send the output, use the `sender-tool:send-file` skill
