from typing import Optional

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.services.parsers import parse_transcript
from app.services.summarizer import annotate_transcript
from app.services.transcriber import transcribe_video


app = FastAPI(title="AI Notes", version="0.1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class AnnotateRequest(BaseModel):
    transcript: str
    summary_length: Optional[str] = "medium"  # short | medium | long


_LENGTH_TO_SENTENCES = {
    "short": 3,
    "medium": 5,
    "long": 8,
}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/annotate")
async def api_annotate(payload: AnnotateRequest):
    raw = (payload.transcript or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Transcript text is required.")

    max_sents = _LENGTH_TO_SENTENCES.get((payload.summary_length or "medium").lower(), 5)
    cleaned = parse_transcript(raw)
    result = annotate_transcript(cleaned, max_summary_sentences=max_sents)
    return JSONResponse(result)


@app.post("/api/transcribe_annotate")
async def api_transcribe_annotate(
    file: UploadFile = File(...),
    summary_length: Optional[str] = Form("medium"),
    language: Optional[str] = Form(None),
    model_size: Optional[str] = Form("small"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Video file is required.")

    import os
    import tempfile

    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        data = await file.read()
        tmp.write(data)
        tmp_path = tmp.name
    try:
        transcript_text = transcribe_video(
            tmp_path, language=language, model_size=(model_size or "small")
        )
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    max_sents = _LENGTH_TO_SENTENCES.get((summary_length or "medium").lower(), 5)
    # No need to run subtitle parser; just clean common noise minimally via summarizer pipeline
    result = annotate_transcript(transcript_text, max_summary_sentences=max_sents)
    return JSONResponse({"transcript": transcript_text, **result})


