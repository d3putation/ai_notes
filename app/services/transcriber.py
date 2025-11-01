from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import threading
from typing import Optional

from faster_whisper import WhisperModel


_model_lock = threading.Lock()
_model_cache: dict[str, WhisperModel] = {}


def _ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg binary not found. Please install ffmpeg and ensure it is on PATH."
        )


def _extract_wav_with_ffmpeg(src_path: str, *, sample_rate: int = 16000, channels: int = 1) -> str:
    _ensure_ffmpeg_available()
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_wav.close()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        src_path,
        "-vn",
        "-ac",
        str(channels),
        "-ar",
        str(sample_rate),
        "-f",
        "wav",
        tmp_wav.name,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        try:
            os.remove(tmp_wav.name)
        except OSError:
            pass
        raise RuntimeError("Failed to extract audio with ffmpeg") from exc
    return tmp_wav.name


def _get_model(model_size: str = "small", compute_type: str = "auto") -> WhisperModel:
    key = f"{model_size}:{compute_type}"
    if key in _model_cache:
        return _model_cache[key]
    with _model_lock:
        if key in _model_cache:
            return _model_cache[key]
        model = WhisperModel(model_size, compute_type=compute_type)
        _model_cache[key] = model
        return model


def transcribe_video(
    file_path: str,
    *,
    language: Optional[str] = None,
    model_size: str = "small",
    vad_filter: bool = False,
) -> str:
    wav_path = _extract_wav_with_ffmpeg(file_path)
    try:
        model = _get_model(model_size=model_size)
        try:
            segments, _ = model.transcribe(
                wav_path,
                language=language,
                vad_filter=vad_filter,
                beam_size=5,
                best_of=5,
            )
        except RuntimeError as e:
            # If VAD requested but onnxruntime not installed, retry without VAD
            if vad_filter and "onnxruntime" in str(e).lower():
                segments, _ = model.transcribe(
                    wav_path,
                    language=language,
                    vad_filter=False,
                    beam_size=5,
                    best_of=5,
                )
            else:
                raise
        texts = []
        for seg in segments:
            t = (seg.text or "").strip()
            if t:
                texts.append(t)
        return " ".join(texts).strip()
    finally:
        try:
            os.remove(wav_path)
        except OSError:
            pass


