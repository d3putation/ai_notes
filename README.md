https://github.com/user-attachments/assets/434343ce-d5aa-41c2-8c8e-860fbe2a5556

<div align="center">

# AI Notes

An AI-powered tool that transforms video conference recordings into actionable meeting summaries, extracting key points, action items, and decisions automatically—all running locally on your machine.

Built for AITEX Summit Fall 2025 - Open Innovation Track

[Installation](#installation) •
[How To Use](#how-to-use) •
[How It Works](#how-it-works) •
[API Documentation](#api-documentation)

</div>

## About This Project

AI Notes addresses a common challenge in modern work: video meetings generate hours of content that requires manual review to extract actionable insights. Using advanced AI technology, we automatically transcribe video conferences and transform the raw audio into structured summaries, key points, action items, and decisions—all processed locally without sending data to external APIs.

## Installation

To get AI Notes running on your machine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone YOUR_GITHUB_REPO_URL
   cd ai_notes
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install --no-deps faster-whisper==1.0.3
   ```

4. **Install FFmpeg (Required for Video Processing):**
   ```bash
   brew install ffmpeg   # macOS
   # Or see: https://ffmpeg.org/download.html
   ```

5. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Verification:**
   - Navigate to http://127.0.0.1:8000 in your web browser
   - You should see the AI Notes interface ready to use

## How To Use

Transform your video conferences into actionable notes in three simple ways:

### Method 1: Upload Video File
1. **Navigate to "From Video" Section:**
   - Click "Upload video" and select your meeting recording (MP4, MOV, WebM, MKV, etc.)

2. **Configure Options (Optional):**
   - Choose summary length: Short, Medium, or Long
   - Specify language code (e.g., "en", "es", "fr") or leave blank for auto-detection

3. **Generate Annotations:**
   - Click "Transcribe & annotate"
   - Wait for processing (transcription may take a moment depending on video length)
   - View results: Summary, Key Points, Keywords, Action Items, and Decisions

### Method 2: Paste Transcript Text
1. **Navigate to "Input Transcript" Section:**
   - Paste or type your meeting transcript directly into the text area

2. **Select Summary Length:**
   - Choose Short, Medium, or Long based on your needs

3. **Generate Annotations:**
   - Click "Generate annotations"
   - Instant results appear below

### Method 3: Load Transcript Files
1. **Use File Input:**
   - Click "Load file" and select a .txt, .srt, or .vtt file
   - The system automatically cleans timestamps and formatting
   - Proceed with annotation as in Method 2

All results are copyable—click the "Copy" button on any section to export the content.

## How It Works

AI Notes combines cutting-edge AI with intelligent audio processing:

**Technical Approach:**
- **Video Processing:** Extracts audio using FFmpeg CLI (no PyAV dependency) and converts to 16kHz mono WAV
- **Speech Transcription:** Leverages Faster Whisper (local Whisper model) for accurate, offline transcription
- **Extractive Summarization:** Scores sentences by word importance (TF-IDF-like approach) and selects top sentences in original order
- **Pattern Detection:** Uses regex patterns to identify action items and decisions from natural language
- **Smart Parsing:** Automatically cleans timestamps, speaker labels, and noise from subtitle files (.srt, .vtt)

**Key Technologies:**
- `faster-whisper` - Local Whisper AI transcription engine
- `ffmpeg` - Audio extraction and processing
- `FastAPI` - Modern Python web framework
- Custom extractive summarization - No external API calls

**Architecture Flow:**
1. Video file uploaded → FFmpeg extracts WAV audio
2. WAV processed → Faster Whisper transcribes speech to text
3. Transcript cleaned → Subtitle parsers remove timestamps/noise
4. Text analyzed → Summarizer extracts key sentences
5. Pattern matching → Actions and decisions identified
6. Results formatted → JSON response with all annotations

## API Documentation

### POST `/api/annotate`

Annotate an existing transcript.

**Request (JSON):**
```json
{
  "transcript": "Your meeting transcript text here...",
  "summary_length": "short | medium | long"  // optional, default: "medium"
}
```

**Response (JSON):**
```json
{
  "summary": "Concise summary of the transcript",
  "key_points": [
    "First important point",
    "Second important point"
  ],
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "actions": [
    "Action item extracted from transcript"
  ],
  "decisions": [
    "Decision made during the meeting"
  ],
  "topics": ["topic1", "topic2"],
  "stats": {
    "num_sentences": 42,
    "num_words": 523
  }
}
```

### POST `/api/transcribe_annotate`

Upload a video file and receive transcription + annotations.

**Request (multipart/form-data):**
- `file`: Video file (MP4, MOV, WebM, MKV, etc.)
- `summary_length`: `"short" | "medium" | "long"` (optional)
- `language`: ISO language code like `"en"`, `"es"` (optional; auto-detect if omitted)
- `model_size`: `"tiny" | "base" | "small" | "medium" | "large"` (optional; default: `"small"`)

**Response (JSON):**
Same structure as `/api/annotate` with an additional field:
```json
{
  "transcript": "Full transcription text...",
  // ... all other fields from /api/annotate
}
```

## Features

✨ **Local Processing** - All AI runs on your machine, no data sent to external APIs  
🎥 **Video Support** - Upload MP4, MOV, WebM, MKV and other video formats  
📄 **Multiple Input Formats** - Works with .txt, .srt, .vtt transcript files  
🤖 **AI Transcription** - Powered by Faster Whisper (local Whisper model)  
📝 **Smart Summarization** - Extractive summarization preserves original meaning  
🎯 **Action Detection** - Automatically identifies action items and decisions  
🔍 **Keyword Extraction** - Key terms and topics highlighted  
⚡️ **Fast Processing** - Optimized for quick turnaround  
🔒 **Privacy-First** - 100% local processing, your data never leaves your machine  
🎨 **Clean UI** - Modern, intuitive web interface

## Use Cases

- **Project Managers:** Quickly extract action items and decisions from team meetings
- **Students:** Transform lecture recordings into study notes with key points
- **Legal Professionals:** Generate summaries from deposition or consultation recordings
- **Journalists:** Extract quotes and key information from interview recordings
- **Researchers:** Analyze focus groups or research interviews for insights
- **Remote Teams:** Maintain clear records of distributed team discussions

## Technical Notes

### Voice Activity Detection (VAD)
VAD is disabled by default to avoid the `onnxruntime` dependency. To enable VAD (which may improve accuracy by filtering non-speech audio):
- macOS (Apple Silicon or Intel): `pip install onnxruntime`
- Linux/CPU: `pip install onnxruntime`
- NVIDIA GPU (Linux/Windows): `pip install onnxruntime-gpu`

If installation fails on newer Python versions, the system automatically falls back to no-VAD mode.

### No PyAV Dependency
The transcriber uses FFmpeg CLI directly, avoiding PyAV build complexity. If you see pip attempting to build `av`, ensure you installed `faster-whisper` with `--no-deps` as shown in installation instructions.

### Summarization Algorithm
- Uses extractive summarization (TF-IDF-like scoring)
- Scores sentences by word importance (stopwords removed)
- Selects highest-scoring sentences in original order
- No external model downloads required

## Project Structure

```
ai_notes/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── services/
│   │   ├── parsers.py       # Transcript parsers (txt/vtt/srt)
│   │   ├── summarizer.py    # Summarization and extraction
│   │   └── transcriber.py   # Video transcription service
│   ├── templates/
│   │   └── index.html       # Web panel UI
│   └── static/
│       └── style.css        # Styling
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## License

See LICENSE file for details.

## Contact

For questions about this project, please open an issue in this repository.

---


