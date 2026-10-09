
import html
import logging
import re

import requests

TRANSLATION_URL = "https://api.mymemory.translated.net/get"
logger = logging.getLogger(__name__)


def split_text(text: str, max_bytes: int = 450) -> list[str]:
    """Split text into segments below the translation API's byte limit."""
    chunks = []
    current = ""

    for word in text.split():
        candidate = f"{current} {word}".strip()

        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
            continue

        if current:
            chunks.append(current)

        # Handle an unusually long individual word safely.
        current = ""
        piece = ""

        for char in word:
            if len((piece + char).encode("utf-8")) > max_bytes:
                if piece:
                    chunks.append(piece)
                piece = char
            else:
                piece += char

        current = piece

    if current:
        chunks.append(current)

    return chunks


def translate_segment(text: str) -> str:
    """Translate one short English segment into Kannada."""
    response = requests.get(
        TRANSLATION_URL,
        params={
            "q": text,
            "langpair": "en|kn",
            "mt": "1",
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("responseStatus") not in (None, 200):
        raise ValueError(
            f"MyMemory response status: {data.get('responseStatus')}; "
            f"{data.get('responseDetails', '')}"
        )

    translated = (
        data.get("responseData", {}).get("translatedText", "")
    )

    translated = html.unescape(translated).strip()

    if not translated:
        raise ValueError("Translation service returned empty text")

    return translated


def translate_to_kannada(text: str) -> str:
    """Translate English text to Kannada, retaining safe fallback behavior."""
    if not text or not text.strip():
        return ""

    try:
        chunks = split_text(text)
        translated_chunks = [
            translate_segment(chunk) for chunk in chunks
        ]
        return " ".join(translated_chunks)

    except Exception:
        logger.exception("Kannada translation failed")
        return text


def translate_result(result: dict) -> dict:
    """Translate prediction information into Kannada."""
    return {
        "language": "kn",
        "disease_name": translate_to_kannada(
            result.get("disease_name", "")
            or result.get("condition", "")
            or result.get("model_class", "")
        ),
        "reason": translate_to_kannada(
            result.get("reason", "")
            or result.get("cause", "")
        ),
        "symptoms": translate_to_kannada(
            result.get("symptoms", "")
        ),
        "treatment": translate_to_kannada(
            result.get("treatment", "")
        ),
        "pesticide": translate_to_kannada(
            result.get("pesticide", "")
        ),
        "message": translate_to_kannada(
            result.get("message", "")
        ),
    }