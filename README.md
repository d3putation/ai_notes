# AI Notes – Video Conference Annotation Panel

https://github.com/user-attachments/assets/434343ce-d5aa-41c2-8c8e-860fbe2a5556

Summarize meeting transcripts into a concise summary, key points, keywords, action items, and decisions. Works locally with no external AI APIs.

## Features
- Paste transcript text or load .txt / .vtt / .srt files
- Cleans timestamps and noise from subtitles
- Extractive summarization (no external model downloads)
- Action/decision detection via patterns
- Simple web panel UI

## Quickstart

1) Create a virtualenv and install deps (no PyAV)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install --no-deps faster-whisper==1.0.3
```




2) Install ffmpeg (required for video/audio decoding)

```bash
brew install ffmpeg   # macOS
# or see: https://ffmpeg.org/download.html
```

3) Run the server

```bash
uvicorn app.main:app --reload
```

4) Open the web panel

- Navigate to `http://127.0.0.1:8000`

## API

POST `/api/annotate`

Request JSON:
```json
{
  "transcript": "string",
  "summary_length": "short | medium | long" // optional, default "medium"
}
```

Response JSON:
```json
{
  "summary": "string",
  "key_points": ["..."],
  "keywords": ["..."],
  "actions": ["..."],
  "decisions": ["..."],
  "topics": ["..."],
  "stats": {"num_sentences": 0, "num_words": 0}
}
```

POST `/api/transcribe_annotate` (multipart form)

Form fields:
- `file`: video file (mp4/mov/webm/mkv...)
- `summary_length`: `short|medium|long` (optional)
- `language`: ISO code like `en`, `es` (optional; auto-detect if omitted)

Response JSON: same as `/api/annotate` plus `transcript` field containing the raw transcription.

## Implementation notes (no av)
- The transcriber calls the `ffmpeg` binary to extract a 16kHz mono WAV from the uploaded video, then passes it to `faster-whisper` for transcription.
- We do not depend on PyAV; if you see pip attempting to build `av`, ensure you installed `faster-whisper` with `--no-deps` as above.

## Notes
- Extractive summarization scores sentences by word importance (stopwords removed) and selects the highest scoring sentences in original order.
- `.vtt` and `.srt` parsers strip timecodes, indices, and common noise like `[music]`.
- For long transcripts, consider running with `summary_length=long` and refining manually if needed.
 - Voice Activity Detection (VAD): Disabled by default to avoid `onnxruntime` dependency. If you want VAD (may reduce non-speech), install ONNX Runtime and it will be used automatically when available:
  - macOS (Apple Silicon or Intel): `pip install onnxruntime`
  - Linux/CPU: `pip install onnxruntime`
  - NVIDIA GPU (Linux/Windows): `pip install onnxruntime-gpu`
  Note: On newer Python versions, a prebuilt wheel may not be available yet. If installation fails, just skip VAD (default) and transcription will still work.

## Project Layout
- `app/main.py` – FastAPI app, routes, and template wiring
- `app/services/parsers.py` – Transcript parsers for txt/vtt/srt
- `app/services/summarizer.py` – Summarization and metadata extraction
- `app/templates/index.html` – Web panel UI
- `app/static/style.css` – Styling

## License
MIT

