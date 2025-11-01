import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


STOPWORDS = {
    "a","about","above","after","again","against","all","am","an","and","any","are","aren't",
    "as","at","be","because","been","before","being","below","between","both","but","by","can't",
    "cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during",
    "each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he",
    "he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how","how's",
    "i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's",
    "me","more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or",
    "other","ought","our","ours","ourselves","out","over","own","same","shan't","she","she'd","she'll",
    "she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs",
    "them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've",
    "this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll",
    "we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while",
    "who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're",
    "you've","your","yours","yourself","yourselves",
}


def split_sentences(text: str) -> List[str]:
    # First split by newlines to respect transcript line breaks, then merge back into sentences
    text = text.replace("\r", "")
    # Guard against missing punctuation by also splitting on long pauses (blank lines already filtered)
    rough = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = []
    for chunk in rough:
        s = chunk.strip()
        if not s:
            continue
        # Remove solo speaker labels like "John:" lines merging next would be better, but keep simple
        sentences.append(s)
    return sentences


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z']+", text.lower())


def build_word_frequencies(sentences: List[str]) -> Counter:
    freq = Counter()
    for s in sentences:
        for w in tokenize(s):
            if w in STOPWORDS:
                continue
            freq[w] += 1
    return freq


def score_sentences(sentences: List[str], word_freq: Counter) -> List[Tuple[int, float]]:
    if not sentences:
        return []
    max_count = max(word_freq.values()) if word_freq else 1
    normalized = {w: c / max_count for w, c in word_freq.items()}
    scored: List[Tuple[int, float]] = []
    for idx, s in enumerate(sentences):
        words = [w for w in tokenize(s) if w not in STOPWORDS]
        if not words:
            scored.append((idx, 0.0))
            continue
        score = sum(normalized.get(w, 0.0) for w in words)
        # Gentle length normalization to avoid very long sentences dominating
        score = score / math.sqrt(len(words) + 1.0)
        scored.append((idx, score))
    return scored


def top_k_sentences(sentences: List[str], scored: List[Tuple[int, float]], k: int) -> List[str]:
    if k <= 0:
        return []
    k = min(k, len(sentences))
    top = sorted(scored, key=lambda t: t[1], reverse=True)[:k]
    # Preserve original order for readability
    top_sorted = sorted(top, key=lambda t: t[0])
    return [sentences[i] for i, _ in top_sorted]


def extract_keywords(text: str, max_keywords: int = 12) -> List[str]:
    words = [w for w in tokenize(text) if w not in STOPWORDS]
    freq = Counter(words)
    # Prefer single words; de-duplicate similar forms naïvely
    keywords = [w for w, _ in freq.most_common(max_keywords * 2)]
    seen_roots = set()
    result: List[str] = []
    for w in keywords:
        root = w.rstrip("s") if len(w) > 4 else w
        if root in seen_roots:
            continue
        seen_roots.add(root)
        result.append(w)
        if len(result) >= max_keywords:
            break
    return result


_ACTION_PATTERNS = [
    r"\bwill\b",
    r"\bneed to\b",
    r"\bshould\b",
    r"\bassign\b",
    r"\btodo\b",
    r"\bby (?:monday|tuesday|wednesday|thursday|friday|eow|eod|\d{1,2}\/(?:\d{1,2}|\d{4}))\b",
    r"\bowner\b",
    r"\baction\b",
    r"\bnext step\b",
]

_DECISION_PATTERNS = [
    r"\bdecided\b",
    r"\bagreed\b",
    r"\bconsensus\b",
    r"\bchoose|chose|chosen\b",
    r"\bconclude|conclusion\b",
    r"\bwe'll go with\b",
    r"\bfinal|finalize|finalised|finalized\b",
]


def extract_matching(sentences: List[str], patterns: List[str], max_items: int = 10) -> List[str]:
    combined = re.compile("|".join(patterns), flags=re.IGNORECASE)
    matches: List[str] = []
    seen = set()
    for s in sentences:
        if combined.search(s):
            normalized = s.strip()
            if normalized not in seen:
                seen.add(normalized)
                matches.append(normalized)
        if len(matches) >= max_items:
            break
    return matches


def annotate_transcript(
    text: str,
    max_summary_sentences: int = 5,
    key_points_multiplier: float = 1.6,
) -> Dict:
    sentences = split_sentences(text)
    stats = {
        "num_sentences": len(sentences),
        "num_words": sum(len(tokenize(s)) for s in sentences),
    }
    freq = build_word_frequencies(sentences)
    scored = score_sentences(sentences, freq)

    summary_sents = top_k_sentences(sentences, scored, max_summary_sentences)
    key_points_k = max(3, min(len(sentences), int(round(max_summary_sentences * key_points_multiplier))))
    key_points = top_k_sentences(sentences, scored, key_points_k)

    keywords = extract_keywords(text, max_keywords=12)
    actions = extract_matching(sentences, _ACTION_PATTERNS, max_items=12)
    decisions = extract_matching(sentences, _DECISION_PATTERNS, max_items=10)

    summary_text = " ".join(summary_sents)

    topics = keywords[:5]

    return {
        "summary": summary_text,
        "key_points": key_points,
        "keywords": keywords,
        "actions": actions,
        "decisions": decisions,
        "topics": topics,
        "stats": stats,
    }


