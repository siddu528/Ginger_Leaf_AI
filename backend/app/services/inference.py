from pathlib import Path
import json
import numpy as np

from ..config import settings, ROOT
from .image_processing import to_model_array


_model = None
_classes = None


# These are the REAL visual classes of the currently trained CNN.
# They must not be falsely mapped to the 20-disease knowledge database.
VISUAL_CLASS_INFO = {
    "Healthy_Ginger": {
        "display_name": "Healthy Ginger Leaf",
        "type": "healthy",
        "cause": "No disease condition was identified by the current CNN visual model.",
        "symptoms": "The uploaded leaf is classified by the current model as healthy ginger.",
        "treatment": "No disease treatment is indicated from this prediction.",
        "pesticide": "No pesticide is recommended for a healthy leaf."
    },

    "Leaf_Blight": {
        "display_name": "Leaf Blight",
        "type": "visual_condition",
        "cause": "The current CNN classified the image as Leaf Blight. A specific causal organism is not verified in the current project database.",
        "symptoms": "The current visual class represents ginger leaf-blight symptoms. Field confirmation is recommended.",
        "treatment": "Remove or isolate severely affected plant material where appropriate and follow a current crop-specific agricultural advisory.",
        "pesticide": "No specific chemical recommendation is supplied by the current project database. Use only a currently registered product according to its label and local agricultural advisory."
    },

    "Dehydrated": {
        "display_name": "Dehydrated / Water-Stressed Leaf",
        "type": "stress_condition",
        "cause": "The current CNN classified the image as dehydrated or water-stressed ginger foliage.",
        "symptoms": "The visual class represents dehydration or water-stress symptoms in the leaf.",
        "treatment": "Check soil moisture and irrigation conditions and follow appropriate ginger crop irrigation practices.",
        "pesticide": "Pesticide treatment is not indicated for dehydration alone."
    },

    "Pest_Damage": {
        "display_name": "Pest Damage",
        "type": "visual_condition",
        "cause": "The current CNN classified the image as showing pest damage. A specific pest species is not identified by this model.",
        "symptoms": "The visual class represents visible damage associated with pest activity.",
        "treatment": "Inspect the plant carefully to identify the pest and follow a current crop-specific integrated pest management advisory.",
        "pesticide": "No specific pesticide is recommended because this CNN does not identify the pest species. Use only a currently registered product according to its label and local advisory."
    }
}


def _load_model_if_present():
    global _model, _classes

    model_path = Path(settings.model_path)

    if not model_path.is_absolute():
        model_path = ROOT / model_path

    if not model_path.exists():
        return None, None

    try:
        import tensorflow as tf

        _model = tf.keras.models.load_model(model_path)

        classes_path = model_path.with_name("class_names.json")

        if classes_path.exists():
            _classes = json.loads(
                classes_path.read_text(encoding="utf-8")
            )

        return _model, _classes

    except Exception:
        return None, None


def predict(image):
    model, classes = _load_model_if_present()

    if model is None or not classes:
        return {
            "success": False,
            "status": "model_not_ready",
            "message": "CNN model is not installed or trained."
        }

    try:
        probs = model.predict(
            to_model_array(image),
            verbose=0
        )[0]

        idx = int(np.argmax(probs))
        confidence = float(probs[idx])

        # Class produced by the trained CNN
        model_class = str(classes[idx])

    except Exception as exc:
        return {
            "success": False,
            "status": "prediction_error",
            "message": f"CNN prediction failed: {str(exc)}"
        }

    # Check confidence before presenting the result.
    if confidence < settings.confidence_threshold:
        return {
            "success": False,
            "status": "low_confidence",
            "message": (
                "The CNN could not confidently classify this image. "
                "Please capture a clearer ginger leaf image."
            ),
            "model_class": model_class,
            "confidence": confidence
        }

    # ---------------------------------------------------------
    # IMPORTANT:
    # These are CNN visual classes, not the G01-G20 disease IDs.
    # ---------------------------------------------------------
    info = VISUAL_CLASS_INFO.get(model_class)

    if info is None:
        return {
            "success": False,
            "status": "unknown_model_class",
            "message": (
                f"The trained CNN returned '{model_class}', "
                "but this visual class is not configured."
            ),
            "model_class": model_class,
            "confidence": confidence
        }

    return {
        "success": True,
        "status": "ok",

        # Actual CNN class
        "model_class": model_class,

        # User-friendly result
        "disease_name": info["display_name"],

        # Keep both names so frontend can use whichever it needs.
        "class_name": model_class,
        "condition_type": info["type"],

        "confidence": confidence,

        "reason": info["cause"],
        "cause": info["cause"],
        "symptoms": info["symptoms"],
        "treatment": info["treatment"],
        "pesticide": info["pesticide"]
    }