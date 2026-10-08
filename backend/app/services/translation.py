import requests


TRANSLATION_URL = "https://api.mymemory.translated.net/get"


def translate_to_kannada(text: str) -> str:
    """
    Translate English text to Kannada using the online translation service.
    If translation fails, return the original English text.
    """

    if not text:
        return ""

    try:
        response = requests.get(
            TRANSLATION_URL,
            params={
                "q": text,
                "langpair": "en|kn",
            },
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        translated = (
            data.get("responseData", {})
            .get("translatedText", "")
        )

        if translated:
            return translated

        return text

    except Exception as error:
        print("Kannada translation error:", error)
        return text


def translate_result(result: dict) -> dict:
    """
    Translate all prediction information into Kannada.
    """

    return {
        "language": "kn",

        "disease_name": translate_to_kannada(
            result.get("condition", "")
            or result.get("model_class", "")
        ),

        "reason": translate_to_kannada(
            result.get("cause", "")
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