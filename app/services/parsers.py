import re
from typing import Literal


TimeFormat = Literal["txt", "srt", "vtt"]


_SRT_TIMECODE_RE = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")
_VTT_TIMECODE_RE = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}")


def detect_format(text: str) -> TimeFormat:
    if not text:
        return "txt"
    head = text.strip().splitlines()[:3]
    joined = "\n".join(head)
    if any(line.strip().upper().startswith("WEBVTT") for line in head) or _VTT_TIMECODE_RE.search(joined):
        return "vtt"
    if _SRT_TIMECODE_RE.search(joined):
        return "srt"
    return "txt"


def _clean_common(text: str) -> str:
    # Remove bracketed noise like [music], (laughs), <c> tags
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = re.sub(r"\([^\)]+\)", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def parse_vtt(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.upper() == "WEBVTT" or s.startswith("NOTE"):
            continue
        if _VTT_TIMECODE_RE.search(s):
            continue
        # Remove cue settings after timecodes if any leaked in
        s = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}.*-->.*\d{2}:\d{2}:\d{2}\.\d{3}", " ", s)
        # Drop line index numbers
        if s.isdigit():
            continue
        cleaned_lines.append(s)
    return _clean_common("\n".join(cleaned_lines))


def parse_srt(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.isdigit():
            continue
        if _SRT_TIMECODE_RE.search(s):
            continue
        cleaned_lines.append(s)
    return _clean_common("\n".join(cleaned_lines))


def parse_txt(text: str) -> str:
    return _clean_common(text)


def parse_transcript(text: str) -> str:
    fmt = detect_format(text)
    if fmt == "vtt":
        return parse_vtt(text)
    if fmt == "srt":
        return parse_srt(text)
    return parse_txt(text)


