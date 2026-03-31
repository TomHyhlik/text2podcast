# text2podcast — Claude Instructions

## "make podcast" workflow

Whenever the user says **"make podcast"** (or similar like "convert to podcast", "make mp3", "podcast this"):

1. Identify the `.md` file from the user's message.
2. Convert it to MP3:
   ```bash
   /home/fuzz/Repos/text2podcast/.venv/bin/python /home/fuzz/Repos/text2podcast/text2podcast.py <file.md>
   ```
   Output MP3 will be placed next to the input file (same name, `.mp3` extension).
3. Send the MP3 via Telegram:
   ```bash
   /home/fuzz/Repos/sender-tool/telegram/send-file.sh --file <output.mp3> --caption "<filename>"
   ```

Do all three steps automatically without asking for confirmation.

## "send it" workflow

Whenever the user says **"send it"** after a podcast has been created, send the most recently generated MP3 using:
```bash
/home/fuzz/Repos/sender-tool/telegram/send-file.sh --file <last_mp3>
```

Telegram config is pre-configured at `/home/fuzz/Repos/sender-tool/telegram/config.json` — no credentials needed.
