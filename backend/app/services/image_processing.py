from io import BytesIO

from PIL import Image, ImageStat

import numpy as np


ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def validate_and_open(
    contents: bytes,
    content_type: str | None,
    max_mb: int,
):
    if content_type not in ALLOWED_TYPES:
        raise ValueError(
            "Only JPG, JPEG, PNG, and WEBP images are accepted."
        )

    if len(contents) > max_mb * 1024 * 1024:
        raise ValueError(
            f"Image exceeds the {max_mb} MB upload limit."
        )

    try:
        # First open the original image and verify it.
        image = Image.open(BytesIO(contents))
        image.verify()

        # Re-open after verify() and convert to RGB.
        image = Image.open(BytesIO(contents)).convert("RGB")

    except Exception as exc:
        raise ValueError(
            "The uploaded file is not a readable image."
        ) from exc

    if min(image.size) < 100:
        raise ValueError(
            "Image resolution is too low. Please use a clearer image."
        )

    stat = ImageStat.Stat(image)

    if sum(stat.mean) / 3 < 8:
        raise ValueError(
            "Image is too dark. Use better lighting."
        )

    return image


def to_model_array(image):
    """
    Preprocessing must match the training pipeline.

    Training:
        image_dataset_from_directory()
        -> 224x224
        -> EfficientNetB0

    Keras EfficientNetB0 includes its own input preprocessing,
    so DO NOT divide the image by 255 here.
    """

    arr = np.asarray(
        image.resize((224, 224)),
        dtype=np.float32,
    )

    return np.expand_dims(arr, axis=0)