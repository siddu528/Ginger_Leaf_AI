
# backend/app/services/translation.py

LANGUAGE = "kn"

KANNADA_CLASS_INFO = {
    "Healthy_Ginger": {
        "display_name": "ಆರೋಗ್ಯಕರ ಶುಂಠಿ ಎಲೆ",
        "cause": "ಪ್ರಸ್ತುತ ಸಿಎನ್‌ಎನ್ ಮಾದರಿಯು ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣವನ್ನು ಗುರುತಿಸಿಲ್ಲ.",
        "symptoms": "ಪ್ರಸ್ತುತ ಮಾದರಿಯು ಈ ಎಲೆಯನ್ನು ಆರೋಗ್ಯಕರ ಶುಂಠಿ ಎಲೆಯೆಂದು ವರ್ಗೀಕರಿಸಿದೆ.",
        "treatment": "ಈ ಮುನ್ಸೂಚನೆಯ ಆಧಾರದ ಮೇಲೆ ರೋಗ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        "pesticide": "ಆರೋಗ್ಯಕರ ಶುಂಠಿ ಎಲೆಗೆ ಯಾವುದೇ ಕೀಟನಾಶಕ ಅಥವಾ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಶಿಫಾರಸು ಮಾಡುವುದಿಲ್ಲ.",
        "message": "ಶುಂಠಿ ಎಲೆ ಆರೋಗ್ಯಕರವಾಗಿದೆ."
    },
    "Leaf_Blight": {
        "display_name": "ಶುಂಠಿ ಎಲೆ ಅಂಗಮಾರಿ ರೋಗ",
        "cause": "ಪ್ರಸ್ತುತ ಸಿಎನ್‌ಎನ್ ಮಾದರಿಯು ಈ ಚಿತ್ರವನ್ನು ಎಲೆ ಅಂಗಮಾರಿ ರೋಗವೆಂದು ವರ್ಗೀಕರಿಸಿದೆ. ನಿರ್ದಿಷ್ಟ ರೋಗಕಾರಕವನ್ನು ಈ ಮಾದರಿಯಿಂದ ಮಾತ್ರ ದೃಢೀಕರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.",
        "symptoms": "ಎಲೆಗಳಲ್ಲಿ ಕಲೆಗಳು, ಬಣ್ಣ ಬದಲಾವಣೆ ಅಥವಾ ಒಣಗುವ ಲಕ್ಷಣಗಳು ಕಾಣಿಸಬಹುದು. ರೋಗವನ್ನು ಖಚಿತಪಡಿಸಲು ಸಸ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ.",
        "treatment": "ತೀವ್ರವಾಗಿ ಬಾಧಿತ ಸಸ್ಯದ ಭಾಗಗಳನ್ನು ಸೂಕ್ತ ರೀತಿಯಲ್ಲಿ ತೆಗೆದುಹಾಕಿ ಅಥವಾ ಪ್ರತ್ಯೇಕಿಸಿ. ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆಯನ್ನು ಅನುಸರಿಸಿ.",
        "pesticide": "ನಿರ್ದಿಷ್ಟ ಔಷಧಿಯನ್ನು ಇಲ್ಲಿ ಶಿಫಾರಸು ಮಾಡಲಾಗುವುದಿಲ್ಲ. ರೋಗವನ್ನು ದೃಢೀಕರಿಸಿ, ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆ ಮತ್ತು ಔಷಧಿಯ ಲೇಬಲ್ ಪ್ರಕಾರ ಅನುಮೋದಿತ ಉತ್ಪನ್ನವನ್ನೇ ಬಳಸಿ.",
        "message": "ಶುಂಠಿ ಎಲೆಯಲ್ಲಿ ಅಂಗಮಾರಿ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ."
    },
    "Dehydrated": {
        "display_name": "ನೀರಿನ ಕೊರತೆಯಿಂದ ಒತ್ತಡಕ್ಕೊಳಗಾದ ಶುಂಠಿ ಎಲೆ",
        "cause": "ಪ್ರಸ್ತುತ ಸಿಎನ್‌ಎನ್ ಮಾದರಿಯು ಈ ಎಲೆಯನ್ನು ನೀರಿನ ಕೊರತೆ ಅಥವಾ ನೀರಿನ ಒತ್ತಡದ ಲಕ್ಷಣಗಳನ್ನು ಹೊಂದಿರುವುದಾಗಿ ವರ್ಗೀಕರಿಸಿದೆ.",
        "symptoms": "ಎಲೆಯಲ್ಲಿ ನೀರಿನ ಕೊರತೆ ಅಥವಾ ನೀರಿನ ಒತ್ತಡದ ಲಕ್ಷಣಗಳು ಕಾಣಿಸಬಹುದು.",
        "treatment": "ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ನೀರಾವರಿ ವ್ಯವಸ್ಥೆಯನ್ನು ಪರಿಶೀಲಿಸಿ. ಶುಂಠಿ ಬೆಳೆಗೆ ಸೂಕ್ತವಾದ ನೀರಾವರಿ ವಿಧಾನಗಳನ್ನು ಅನುಸರಿಸಿ.",
        "pesticide": "ನೀರಿನ ಕೊರತೆಯೊಂದೇ ಸಮಸ್ಯೆಯಾಗಿದ್ದರೆ ಕೀಟನಾಶಕ ಚಿಕಿತ್ಸೆಯ ಅಗತ್ಯವಿಲ್ಲ.",
        "message": "ಶುಂಠಿ ಎಲೆಯಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ."
    },
    "Pest_Damage": {
        "display_name": "ಕೀಟಗಳಿಂದ ಹಾನಿಗೊಳಗಾದ ಶುಂಠಿ ಎಲೆ",
        "cause": "ಪ್ರಸ್ತುತ ಸಿಎನ್‌ಎನ್ ಮಾದರಿಯು ಈ ಎಲೆಯಲ್ಲಿ ಕೀಟ ಹಾನಿಯ ಲಕ್ಷಣಗಳಿವೆ ಎಂದು ವರ್ಗೀಕರಿಸಿದೆ. ನಿರ್ದಿಷ್ಟ ಕೀಟದ ಜಾತಿಯನ್ನು ಈ ಮಾದರಿ ಗುರುತಿಸುವುದಿಲ್ಲ.",
        "symptoms": "ಎಲೆಯಲ್ಲಿ ಕೀಟಗಳ ಚಟುವಟಿಕೆಗೆ ಸಂಬಂಧಿಸಿದ ಹಾನಿಯ ಲಕ್ಷಣಗಳು ಕಾಣಿಸಬಹುದು.",
        "treatment": "ಕೀಟವನ್ನು ಗುರುತಿಸಲು ಸಸ್ಯವನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಪರಿಶೀಲಿಸಿ. ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರ ಸಮಗ್ರ ಕೀಟ ನಿರ್ವಹಣಾ ಸಲಹೆಯನ್ನು ಅನುಸರಿಸಿ.",
        "pesticide": "ಈ ಮಾದರಿಯು ನಿರ್ದಿಷ್ಟ ಕೀಟವನ್ನು ಗುರುತಿಸುವುದಿಲ್ಲವಾದ್ದರಿಂದ ನಿರ್ದಿಷ್ಟ ಕೀಟನಾಶಕವನ್ನು ಶಿಫಾರಸು ಮಾಡಲಾಗುವುದಿಲ್ಲ. ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆಯಂತೆ ಅನುಮೋದಿತ ಉತ್ಪನ್ನವನ್ನೇ ಬಳಸಿ.",
        "message": "ಶುಂಠಿ ಎಲೆಯಲ್ಲಿ ಕೀಟ ಹಾನಿಯ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ."
    }
}


def translate_result(result):
    """Translate prediction fields into Kannada without network access."""

    if not isinstance(result, dict):
        return {
            "language": LANGUAGE,
            "disease_name": "",
            "reason": "",
            "symptoms": "",
            "treatment": "",
            "pesticide": "",
            "message": "ಅಮಾನ್ಯ ಫಲಿತಾಂಶದ ಮಾಹಿತಿ."
        }

    model_class = result.get("model_class") or result.get("class_name")
    info = KANNADA_CLASS_INFO.get(model_class)

    if info is None:
        return {
            "language": LANGUAGE,
            "disease_name": "ವರ್ಗೀಕರಣ ಲಭ್ಯವಿಲ್ಲ",
            "reason": "ಈ ವರ್ಗಕ್ಕೆ ಕನ್ನಡ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",
            "symptoms": "",
            "treatment": "",
            "pesticide": "",
            "message": "ಮಾದರಿಯ ವರ್ಗದ ಹೆಸರನ್ನು ಪರಿಶೀಲಿಸಿ."
        }

    # Do not show treatment advice as a confirmed diagnosis
    # when the model's confidence is below the configured threshold.
    if result.get("success") is not True:
        message = (
            "ಚಿತ್ರವನ್ನು ವಿಶ್ವಾಸಾರ್ಹವಾಗಿ ವರ್ಗೀಕರಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ. "
            "ದಯವಿಟ್ಟು ಸ್ಪಷ್ಟವಾದ ಶುಂಠಿ ಎಲೆಯ ಚಿತ್ರವನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ."
        )
        return {
            "language": LANGUAGE,
            "disease_name": info["display_name"],
            "reason": info["cause"],
            "symptoms": info["symptoms"],
            "treatment": "",
            "pesticide": "",
            "message": message
        }

    return {
        "language": LANGUAGE,
        "disease_name": info["display_name"],
        "reason": info["cause"],
        "symptoms": info["symptoms"],
        "treatment": info["treatment"],
        "pesticide": info["pesticide"],
        "message": info["message"]
    }

def translate_to_kannada(text):
    """
    Compatibility function for the existing translation router.
    Accepts text and returns it unchanged if no text translator is configured.
    """
    if text is None:
        return ""
    return str(text)
