import ctypes
import json
import time
from pathlib import Path
from ctypes import wintypes

import cv2
import numpy as np
import tensorflow as tf


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"
CONFIG_FILE = BASE_DIR / "config" / "diseases.json"

INPUT_SIZE = (224, 224)

# ------------------------------------------------------------
# LIVE DETECTION THRESHOLD
# ------------------------------------------------------------
# 60% or higher = confirmed
# Below 60% = NOT CONFIRMED
THRESHOLD = 0.60

WEBCAM_INDEX = 0

# Run inference every detected frame.
INFERENCE_EVERY_N_FRAMES = 1

# Disease preference order.
# If multiple models cross the threshold, the first one wins.
DISEASE_ORDER = [
    "Disease_1",
    "Disease_2",
    "Disease_3",
    "Disease_4",
    "Disease_5",
    "Disease_6",
    "Disease_7",
]


# ============================================================
# WINDOWS KANNADA / UNICODE RENDERING
# ============================================================

IS_WINDOWS = False

try:
    IS_WINDOWS = (
        __import__("platform").system().lower()
        == "windows"
    )
except Exception:
    IS_WINDOWS = False


if IS_WINDOWS:

    # --------------------------------------------------------
    # Windows DLLs
    #
    # IMPORTANT:
    # DrawTextW belongs to USER32.DLL.
    # It does NOT belong to GDI32.DLL.
    # --------------------------------------------------------

    gdi32 = ctypes.WinDLL(
        "gdi32.dll",
        use_last_error=True
    )

    user32 = ctypes.WinDLL(
        "user32.dll",
        use_last_error=True
    )

    # --------------------------------------------------------
    # Constants
    # --------------------------------------------------------

    BI_RGB = 0
    DIB_RGB_COLORS = 0

    TRANSPARENT = 1

    DT_LEFT = 0x00000000
    DT_TOP = 0x00000000
    DT_WORDBREAK = 0x00000010
    DT_NOPREFIX = 0x00000800
    DT_CALCRECT = 0x00000400

    # --------------------------------------------------------
    # Windows structures
    # --------------------------------------------------------

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            (
                "biSize",
                wintypes.DWORD
            ),
            (
                "biWidth",
                wintypes.LONG
            ),
            (
                "biHeight",
                wintypes.LONG
            ),
            (
                "biPlanes",
                wintypes.WORD
            ),
            (
                "biBitCount",
                wintypes.WORD
            ),
            (
                "biCompression",
                wintypes.DWORD
            ),
            (
                "biSizeImage",
                wintypes.DWORD
            ),
            (
                "biXPelsPerMeter",
                wintypes.LONG
            ),
            (
                "biYPelsPerMeter",
                wintypes.LONG
            ),
            (
                "biClrUsed",
                wintypes.DWORD
            ),
            (
                "biClrImportant",
                wintypes.DWORD
            ),
        ]


    class RGBQUAD(ctypes.Structure):
        _fields_ = [
            (
                "rgbBlue",
                wintypes.BYTE
            ),
            (
                "rgbGreen",
                wintypes.BYTE
            ),
            (
                "rgbRed",
                wintypes.BYTE
            ),
            (
                "rgbReserved",
                wintypes.BYTE
            ),
        ]


    class BITMAPINFO(ctypes.Structure):
        _fields_ = [
            (
                "bmiHeader",
                BITMAPINFOHEADER
            ),
            (
                "bmiColors",
                RGBQUAD * 1
            ),
        ]


    # --------------------------------------------------------
    # Function signatures
    # --------------------------------------------------------

    user32.DrawTextW.argtypes = [
        wintypes.HDC,
        wintypes.LPCWSTR,
        ctypes.c_int,
        ctypes.POINTER(wintypes.RECT),
        wintypes.UINT,
    ]

    user32.DrawTextW.restype = ctypes.c_int

    gdi32.CreateCompatibleDC.argtypes = [
        wintypes.HDC
    ]

    gdi32.CreateCompatibleDC.restype = wintypes.HDC

    gdi32.DeleteDC.argtypes = [
        wintypes.HDC
    ]

    gdi32.DeleteDC.restype = wintypes.BOOL

    gdi32.CreateDIBSection.argtypes = [
        wintypes.HDC,
        ctypes.POINTER(BITMAPINFO),
        wintypes.UINT,
        ctypes.POINTER(ctypes.c_void_p),
        wintypes.HANDLE,
        wintypes.DWORD,
    ]

    gdi32.CreateDIBSection.restype = wintypes.HANDLE

    gdi32.SelectObject.argtypes = [
        wintypes.HDC,
        wintypes.HGDIOBJ,
    ]

    gdi32.SelectObject.restype = wintypes.HGDIOBJ

    gdi32.DeleteObject.argtypes = [
        wintypes.HGDIOBJ
    ]

    gdi32.DeleteObject.restype = wintypes.BOOL

    gdi32.CreateFontW.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.LPCWSTR,
    ]

    gdi32.CreateFontW.restype = wintypes.HGDIOBJ

    gdi32.SetBkMode.argtypes = [
        wintypes.HDC,
        ctypes.c_int,
    ]

    gdi32.SetBkMode.restype = ctypes.c_int

    gdi32.SetTextColor.argtypes = [
        wintypes.HDC,
        wintypes.DWORD,
    ]

    gdi32.SetTextColor.restype = wintypes.DWORD


    # --------------------------------------------------------
    # Render Unicode using Windows
    # --------------------------------------------------------

    def render_windows_text(
        text,
        width,
        height,
        font_size=24,
        text_color=(230, 230, 230),
        font_name="Nirmala UI"
    ):
        """
        Render Unicode/Kannada text into a NumPy BGR image.

        The original layout, positions and panel sizes are preserved.
        Only the Kannada/Unicode renderer is improved so long text
        automatically reduces its font size until it fits inside the
        existing height.
        """

        width = max(1, int(width))
        height = max(1, int(height))
        font_size = max(8, int(font_size))

        # ----------------------------------------------------
        # Create compatible DC
        # ----------------------------------------------------

        hdc = gdi32.CreateCompatibleDC(
            None
        )

        if not hdc:
            return np.zeros(
                (height, width, 3),
                dtype=np.uint8
            )

        # ----------------------------------------------------
        # Create top-down 32-bit bitmap
        # ----------------------------------------------------

        bmi = BITMAPINFO()

        bmi.bmiHeader.biSize = ctypes.sizeof(
            BITMAPINFOHEADER
        )

        bmi.bmiHeader.biWidth = width

        # Negative height = top-down bitmap.
        bmi.bmiHeader.biHeight = -height

        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = BI_RGB

        bits = ctypes.c_void_p()

        hbitmap = gdi32.CreateDIBSection(
            hdc,
            ctypes.byref(bmi),
            DIB_RGB_COLORS,
            ctypes.byref(bits),
            None,
            0
        )

        if not hbitmap or not bits:
            gdi32.DeleteDC(hdc)

            return np.zeros(
                (height, width, 3),
                dtype=np.uint8
            )

        old_bitmap = gdi32.SelectObject(
            hdc,
            hbitmap
        )

        # ----------------------------------------------------
        # Clear bitmap
        # ----------------------------------------------------

        ctypes.memset(
            bits,
            0,
            width * height * 4
        )

        # ----------------------------------------------------
        # Create Nirmala UI font
        #
        # Nirmala UI supports Kannada on Windows.
        # ----------------------------------------------------

        def create_font(size):
            return gdi32.CreateFontW(
                -int(size),
                0,
                0,
                0,
                400,
                0,
                0,
                0,
                0,
                0,
                0,
                5,
                0,
                font_name
            )

        hfont = create_font(font_size)

        if not hfont:

            gdi32.SelectObject(
                hdc,
                old_bitmap
            )

            gdi32.DeleteObject(
                hbitmap
            )

            gdi32.DeleteDC(
                hdc
            )

            return np.zeros(
                (height, width, 3),
                dtype=np.uint8
            )

        old_font = gdi32.SelectObject(
            hdc,
            hfont
        )

        # ----------------------------------------------------
        # Transparent background
        # ----------------------------------------------------

        gdi32.SetBkMode(
            hdc,
            TRANSPARENT
        )

        # ----------------------------------------------------
        # Text color
        #
        # Windows COLORREF:
        # 0x00BBGGRR
        # ----------------------------------------------------

        r, g, b = text_color

        colorref = (
            (int(b) << 16)
            | (int(g) << 8)
            | int(r)
        )

        gdi32.SetTextColor(
            hdc,
            colorref
        )

        text_value = str(text)

        # ----------------------------------------------------
        # AUTO-FIT KANNADA TEXT
        #
        # The caller's width/height are NOT changed.
        # If Kannada text needs more lines than the existing
        # box can hold, reduce only the font size.
        # ----------------------------------------------------

        fitted_font_size = font_size

        while fitted_font_size > 12:
            measure_rect = wintypes.RECT(
                0,
                0,
                width,
                height
            )

            user32.DrawTextW(
                hdc,
                text_value,
                -1,
                ctypes.byref(measure_rect),
                (
                    DT_LEFT
                    | DT_TOP
                    | DT_WORDBREAK
                    | DT_NOPREFIX
                    | DT_CALCRECT
                )
            )

            required_height = (
                measure_rect.bottom
                - measure_rect.top
            )

            if required_height <= height - 4:
                break

            # Replace the current font with a smaller one.
            gdi32.SelectObject(
                hdc,
                old_font
            )

            gdi32.DeleteObject(
                hfont
            )

            fitted_font_size -= 1

            hfont = create_font(
                fitted_font_size
            )

            if not hfont:
                break

            old_font = gdi32.SelectObject(
                hdc,
                hfont
            )

            gdi32.SetBkMode(
                hdc,
                TRANSPARENT
            )

            gdi32.SetTextColor(
                hdc,
                colorref
            )

        # ----------------------------------------------------
        # Draw Unicode text
        #
        # IMPORTANT:
        # DrawTextW is from USER32, NOT GDI32.
        # ----------------------------------------------------

        rect = wintypes.RECT(
            0,
            0,
            width,
            height
        )

        user32.DrawTextW(
            hdc,
            text_value,
            -1,
            ctypes.byref(rect),
            (
                DT_LEFT
                | DT_TOP
                | DT_WORDBREAK
                | DT_NOPREFIX
            )
        )

        # ----------------------------------------------------
        # Copy pixels to NumPy
        # ----------------------------------------------------

        buffer_size = (
            width
            * height
            * 4
        )

        raw = ctypes.string_at(
            bits,
            buffer_size
        )

        image = np.frombuffer(
            raw,
            dtype=np.uint8
        ).reshape(
            (height, width, 4)
        ).copy()

        # GDI bitmap = BGRA.
        bgr = image[:, :, :3]

        # ----------------------------------------------------
        # Cleanup
        # ----------------------------------------------------

        gdi32.SelectObject(
            hdc,
            old_font
        )

        gdi32.DeleteObject(
            hfont
        )

        gdi32.SelectObject(
            hdc,
            old_bitmap
        )

        gdi32.DeleteObject(
            hbitmap
        )

        gdi32.DeleteDC(
            hdc
        )

        return bgr


else:

    def render_windows_text(
        text,
        width,
        height,
        font_size=24,
        text_color=(230, 230, 230),
        font_name="Nirmala UI"
    ):
        return np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )


# ============================================================
# DRAW UNICODE TEXT
# ============================================================

def draw_unicode_text(
    image,
    text,
    x,
    y,
    width,
    height,
    font_size=24,
    color=(230, 230, 230)
):
    """
    Draw Unicode/Kannada text onto an OpenCV image.
    """

    rendered = render_windows_text(
        text,
        width,
        height,
        font_size,
        color
    )

    rendered_h, rendered_w = (
        rendered.shape[:2]
    )

    image_h, image_w = image.shape[:2]

    x = int(x)
    y = int(y)

    if x >= image_w or y >= image_h:
        return

    if x < 0 or y < 0:
        return

    usable_w = min(
        rendered_w,
        image_w - x
    )

    usable_h = min(
        rendered_h,
        image_h - y
    )

    if usable_w <= 0 or usable_h <= 0:
        return

    rendered = rendered[
        :usable_h,
        :usable_w
    ]

    target = image[
        y:y + usable_h,
        x:x + usable_w
    ]

    # --------------------------------------------------------
    # Transparent mask.
    #
    # Black pixels are considered background.
    # --------------------------------------------------------

    mask = np.any(
        rendered > 0,
        axis=2
    )

    target[mask] = rendered[mask]


# ============================================================
# LOAD DISEASE CONFIGURATION
# ============================================================

def load_disease_config():

    if not CONFIG_FILE.exists():

        print(
            f"WARNING: Disease config not found: "
            f"{CONFIG_FILE}"
        )

        return {}

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return data

    except Exception as e:

        print(
            f"ERROR reading diseases.json: {e}"
        )

        return {}


disease_config = load_disease_config()


# ============================================================
# GET DISEASE INFORMATION
# ============================================================

def get_disease_info(disease_id):

    info = disease_config.get(
        disease_id,
        {}
    )

    # English
    display_name = info.get(
        "display_name",
        disease_id
    )

    reason = info.get(
        "reason",
        info.get(
            "symptoms",
            "Disease information not configured."
        )
    )

    pesticide = info.get(
        "pesticide",
        info.get(
            "solution",
            ""
        )
    )

    # Kannada
    display_name_kn = info.get(
        "display_name_kn",
        display_name
    )

    reason_kn = info.get(
        "reason_kn",
        reason
    )

    pesticide_kn = info.get(
        "pesticide_kn",
        pesticide
    )

    return {
        "display_name": display_name,
        "display_name_kn": display_name_kn,
        "reason": reason,
        "reason_kn": reason_kn,
        "pesticide": pesticide,
        "pesticide_kn": pesticide_kn,
    }


# ============================================================
# LOAD ALL AVAILABLE MODELS
# ============================================================

def load_models():

    loaded_models = {}

    for i in range(1, 8):

        disease_id = (
            f"Disease_{i}"
        )

        model_path = (
            MODEL_DIR
            / f"{disease_id}.keras"
        )

        if not model_path.exists():

            print(
                f"  {disease_id}: "
                f"model not found - skipped"
            )

            continue

        try:

            print(
                f"Loading {disease_id}..."
            )

            model = (
                tf.keras.models.load_model(
                    model_path,
                    compile=False
                )
            )

            loaded_models[
                disease_id
            ] = model

            print(
                f"  Loaded: {model_path}"
            )

        except Exception as e:

            print(
                f"  ERROR loading "
                f"{disease_id}: {e}"
            )

    return loaded_models


models = load_models()


if not models:

    print(
        "\nERROR: No trained disease "
        "models were found."
    )

    print(
        "Train at least one model first."
    )

    raise SystemExit(1)


print(
    "\nAvailable disease models:"
)

for disease_id in models:

    print(
        f"  - {disease_id}"
    )

print()


# ============================================================
# LANGUAGE SELECTION
# ============================================================

def choose_language():

    print(
        "Language selection"
    )

    print(
        "1. English"
    )

    print(
        "2. Kannada"
    )

    while True:

        choice = input(
            "Enter choice (1 or 2): "
        ).strip()

        if choice == "1":

            print(
                "English selected."
            )

            return "en"

        if choice == "2":

            print(
                "Kannada selected."
            )

            return "kn"

        print(
            "Please enter 1 or 2."
        )


# ============================================================
# GINGER LEAF DETECTION
# ============================================================

def detect_leaf(frame):
    """
    Starter HSV/contour ginger leaf detector.

    This is only a development gate.
    It can later be replaced by a trained YOLO detector.
    """

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    # Broad green vegetation range.
    lower_green = np.array(
        [25, 30, 30],
        dtype=np.uint8
    )

    upper_green = np.array(
        [100, 255, 255],
        dtype=np.uint8
    )

    mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, None

    frame_h, frame_w = (
        frame.shape[:2]
    )

    frame_area = (
        frame_h * frame_w
    )

    best_contour = None
    best_area = 0

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < 2000:
            continue

        if area > frame_area * 0.90:
            continue

        x, y, w, h = (
            cv2.boundingRect(contour)
        )

        if w < 40 or h < 40:
            continue

        if area > best_area:

            best_area = area
            best_contour = contour

    if best_contour is None:
        return None, None

    x, y, w, h = (
        cv2.boundingRect(
            best_contour
        )
    )

    margin = 10

    x1 = max(
        0,
        x - margin
    )

    y1 = max(
        0,
        y - margin
    )

    x2 = min(
        frame_w,
        x + w + margin
    )

    y2 = min(
        frame_h,
        y + h + margin
    )

    crop = frame[
        y1:y2,
        x1:x2
    ]

    if crop.size == 0:
        return None, None

    return (
        crop,
        (x1, y1, x2, y2)
    )


# ============================================================
# PREPROCESS LEAF
# ============================================================

def preprocess_leaf(leaf):

    rgb = cv2.cvtColor(
        leaf,
        cv2.COLOR_BGR2RGB
    )

    resized = cv2.resize(
        rgb,
        INPUT_SIZE,
        interpolation=cv2.INTER_AREA
    )

    tensor = np.expand_dims(
        resized.astype(
            np.float32
        ),
        axis=0
    )

    return tensor


# ============================================================
# RUN EVERY AVAILABLE DISEASE MODEL
# ============================================================

def predict_all_models(leaf):

    input_tensor = (
        preprocess_leaf(leaf)
    )

    predictions = {}

    print(
        "\n"
        + "=" * 16
        + " MODEL PREDICTIONS "
        + "=" * 16
    )

    for disease_id in DISEASE_ORDER:

        if disease_id not in models:
            continue

        model = models[
            disease_id
        ]

        try:

            output = model.predict(
                input_tensor,
                verbose=0
            )

            probability = float(
                np.asarray(
                    output
                ).reshape(-1)[0]
            )

            probability = max(
                0.0,
                min(
                    1.0,
                    probability
                )
            )

            predictions[
                disease_id
            ] = probability

            print(
                f"{disease_id} raw output: "
                f"{probability:.6f}"
            )

            print(
                f"{disease_id}: "
                f"{probability * 100:.2f}%"
            )

        except Exception as e:

            print(
                f"Prediction error for "
                f"{disease_id}: {e}"
            )

    print(
        "=" * 50
    )

    return predictions


# ============================================================
# SELECT RESULT
# ============================================================

def select_result(predictions):

    if not predictions:

        return (
            None,
            0.0,
            False
        )

    confirmed = []

    # --------------------------------------------------------
    # Check ALL available models.
    # --------------------------------------------------------

    for disease_id in DISEASE_ORDER:

        if disease_id not in predictions:
            continue

        probability = (
            predictions[disease_id]
        )

        if probability >= THRESHOLD:

            confirmed.append(
                (
                    disease_id,
                    probability
                )
            )

    # --------------------------------------------------------
    # Preference order.
    # --------------------------------------------------------

    if confirmed:

        for disease_id in DISEASE_ORDER:

            for candidate_id, probability in confirmed:

                if candidate_id == disease_id:

                    return (
                        candidate_id,
                        probability,
                        True
                    )

    # --------------------------------------------------------
    # Nothing crossed threshold.
    #
    # Return closest disease.
    # --------------------------------------------------------

    closest_id = max(
        predictions,
        key=predictions.get
    )

    closest_probability = (
        predictions[closest_id]
    )

    return (
        closest_id,
        closest_probability,
        False
    )


# ============================================================
# ENGLISH WRAPPED TEXT
# ============================================================

def draw_wrapped_text(
    image,
    text,
    x,
    y,
    max_width,
    font,
    scale,
    color,
    thickness=1,
    line_gap=22
):

    words = str(text).split()

    lines = []

    current = ""

    for word in words:

        test = (
            word
            if not current
            else current + " " + word
        )

        text_size = cv2.getTextSize(
            test,
            font,
            scale,
            thickness
        )[0]

        if text_size[0] <= max_width:

            current = test

        else:

            if current:
                lines.append(
                    current
                )

            current = word

    if current:
        lines.append(
            current
        )

    for line in lines:

        cv2.putText(
            image,
            line,
            (x, y),
            font,
            scale,
            color,
            thickness,
            cv2.LINE_AA
        )

        y += line_gap

    return y


# ============================================================
# DRAW RESULT PANEL
# ============================================================

def draw_result_panel(
    panel,
    disease_id,
    probability,
    confirmed,
    language
):

    h, w = panel.shape[:2]

    font = cv2.FONT_HERSHEY_SIMPLEX

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    if language == "kn":

        draw_unicode_text(
            panel,
            "ಶುಂಠಿ ಎಲೆ ರೋಗ ಪತ್ತೆ AI",
            20,
            15,
            w - 40,
            55,
            28,
            (255, 255, 255)
        )

    else:

        cv2.putText(
            panel,
            "GINGER LEAF DISEASE AI",
            (20, 40),
            font,
            0.75,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

    if disease_id is None:

        if language == "kn":

            draw_unicode_text(
                panel,
                "ಫಲಿತಾಂಶ ಲಭ್ಯವಿಲ್ಲ",
                20,
                85,
                w - 40,
                60,
                28,
                (255, 255, 255)
            )

        else:

            cv2.putText(
                panel,
                "No result",
                (20, 100),
                font,
                0.8,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        return

    info = get_disease_info(
        disease_id
    )

    if language == "kn":

        display_name = info[
            "display_name_kn"
        ]

        reason = info[
            "reason_kn"
        ]

        pesticide = info[
            "pesticide_kn"
        ]

    else:

        display_name = info[
            "display_name"
        ]

        reason = info[
            "reason"
        ]

        pesticide = info[
            "pesticide"
        ]

    # ========================================================
    # CONFIRMED
    # ========================================================

    if confirmed:

        if language == "kn":

            draw_unicode_text(
                panel,
                "ರೋಗ ಪತ್ತೆಯಾಗಿದೆ",
                20,
                70,
                w - 40,
                55,
                30,
                (0, 255, 0)
            )

            draw_unicode_text(
                panel,
                display_name,
                20,
                125,
                w - 40,
                65,
                27,
                (255, 255, 255)
            )

            draw_unicode_text(
                panel,
                f"ವಿಶ್ವಾಸ: {probability * 100:.1f}%",
                20,
                185,
                w - 40,
                55,
                24,
                (255, 255, 255)
            )

            draw_unicode_text(
                panel,
                "ಕಾರಣ:",
                20,
                245,
                w - 40,
                45,
                24,
                (255, 255, 255)
            )

            draw_unicode_text(
                panel,
                reason,
                20,
                290,
                w - 40,
                130,
                20,
                (220, 220, 220)
            )

            if pesticide:

                draw_unicode_text(
                    panel,
                    "ಕೀಟನಾಶಕ / ಶಿಲೀಂಧ್ರನಾಶಕ:",
                    20,
                    430,
                    w - 40,
                    55,
                    22,
                    (255, 255, 255)
                )

                draw_unicode_text(
                    panel,
                    pesticide,
                    20,
                    480,
                    w - 40,
                    130,
                    20,
                    (220, 220, 220)
                )

        else:

            cv2.putText(
                panel,
                "DISEASE DETECTED",
                (20, 90),
                font,
                0.85,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                display_name,
                (20, 130),
                font,
                0.75,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                (
                    f"Confidence: "
                    f"{probability * 100:.1f}%"
                ),
                (20, 165),
                font,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            y = 205

            cv2.putText(
                panel,
                "Reason:",
                (20, y),
                font,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            y += 28

            y = draw_wrapped_text(
                panel,
                reason,
                20,
                y,
                w - 40,
                font,
                0.48,
                (220, 220, 220),
                1,
                20
            )

            y += 15

            cv2.putText(
                panel,
                "Pesticide / Fungicide:",
                (20, y),
                font,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            y += 28

            draw_wrapped_text(
                panel,
                pesticide,
                20,
                y,
                w - 40,
                font,
                0.48,
                (220, 220, 220),
                1,
                20
            )

    # ========================================================
    # NOT CONFIRMED
    # ========================================================

    else:

        if language == "kn":

            draw_unicode_text(
                panel,
                "ಫಲಿತಾಂಶ ಖಚಿತವಾಗಿಲ್ಲ",
                20,
                75,
                w - 40,
                60,
                28,
                (0, 165, 255)
            )

            draw_unicode_text(
                panel,
                f"ಹತ್ತಿರದ ರೋಗ: {display_name}",
                20,
                140,
                w - 40,
                70,
                23,
                (255, 255, 255)
            )

            draw_unicode_text(
                panel,
                f"ವಿಶ್ವಾಸ: {probability * 100:.1f}%",
                20,
                215,
                w - 40,
                50,
                23,
                (255, 255, 255)
            )

            draw_unicode_text(
                panel,
                f"ಅಗತ್ಯ ಮಿತಿ: {THRESHOLD * 100:.0f}%",
                20,
                275,
                w - 40,
                50,
                22,
                (255, 255, 255)
            )

            draw_unicode_text(
                panel,
                "ಹೆಚ್ಚು ಸ್ಪಷ್ಟವಾದ ಎಲೆ ಚಿತ್ರವನ್ನು ನೀಡಿ.",
                20,
                335,
                w - 40,
                70,
                21,
                (220, 220, 220)
            )

        else:

            cv2.putText(
                panel,
                "RESULT: NOT CONFIRMED",
                (20, 90),
                font,
                0.75,
                (0, 165, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                f"Closest: {display_name}",
                (20, 130),
                font,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                (
                    f"Confidence: "
                    f"{probability * 100:.1f}%"
                ),
                (20, 165),
                font,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                (
                    f"Required: "
                    f"{THRESHOLD * 100:.0f}%"
                ),
                (20, 200),
                font,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                "Please capture a clearer leaf image.",
                (20, 240),
                font,
                0.5,
                (220, 220, 220),
                1,
                cv2.LINE_AA
            )


# ============================================================
# DRAW MODEL PROBABILITIES
# ============================================================

def draw_model_probabilities(
    panel,
    predictions,
    language
):

    if not predictions:
        return

    h, w = panel.shape[:2]

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Put ALL available model probabilities in a compact
    # bottom section. Do not use a fixed Y position because
    # camera resolutions can be smaller than 720 pixels.
    row_height = 22

    start_y = (
        h
        - (
            len(predictions)
            * row_height
        )
        - 30
    )

    # Keep the section inside the panel for 480p/720p/etc.
    start_y = max(260, start_y)

    # If there is not enough room, still draw the rows
    # from the bottom instead of hiding the whole section.
    if start_y >= h:
        start_y = max(20, h - (len(predictions) * row_height) - 5)

    if language == "kn":

        draw_unicode_text(
            panel,
            "ಮಾದರಿ ಫಲಿತಾಂಶಗಳು:",
            20,
            start_y,
            w - 40,
            40,
            20,
            (200, 200, 200)
        )

    else:

        cv2.putText(
            panel,
            "MODEL CHECK:",
            (20, start_y + 18),
            font,
            0.5,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

    y = start_y + 30

    for disease_id in DISEASE_ORDER:

        if disease_id not in predictions:
            continue

        probability = (
            predictions[disease_id]
        )

        info = get_disease_info(
            disease_id
        )

        if language == "kn":

            text_value = (
                f"{info['display_name_kn']}: "
                f"{probability * 100:.1f}%"
            )

            draw_unicode_text(
                panel,
                text_value,
                20,
                y,
                w - 40,
                row_height,
                16,
                (200, 200, 200)
            )

        else:

            cv2.putText(
                panel,
                (
                    f"{disease_id}: "
                    f"{probability * 100:.1f}%"
                ),
                (20, y + 16),
                font,
                0.40,
                (200, 200, 200),
                1,
                cv2.LINE_AA
            )

        y += row_height

        if y >= h - 5:
            break


# ============================================================
# CAMERA SELECTION
# ============================================================

def choose_camera():

    print(
        "Camera selection"
    )

    print(
        "1. Laptop webcam"
    )

    print(
        "2. ESP32-CAM"
    )

    while True:

        choice = input(
            "Enter choice (1 or 2): "
        ).strip()

        if choice == "1":

            return cv2.VideoCapture(
                WEBCAM_INDEX
            )

        if choice == "2":

            url = input(
                "Enter ESP32-CAM stream URL: "
            ).strip()

            if not url:

                print(
                    "ERROR: ESP32-CAM URL "
                    "cannot be empty."
                )

                continue

            print(
                f"Connecting to: {url}"
            )

            return cv2.VideoCapture(
                url
            )

        print(
            "Please enter 1 or 2."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    language = choose_language()

    print()

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    cap = choose_camera()

    if not cap.isOpened():

        print(
            "\nERROR: Could not open camera."
        )

        print(
            "Check your webcam or "
            "ESP32-CAM URL."
        )

        return

    print()

    print(
        "Camera started."
    )

    print(
        "Press Q to quit."
    )

    print()

    frame_count = 0

    last_predictions = {}

    last_result_id = None

    last_result_probability = 0.0

    last_result_confirmed = False

    previous_time = time.time()

    fps = 0.0

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "ERROR: Could not read "
                "camera frame."
            )

            break

        frame_count += 1

        # ----------------------------------------------------
        # Detect ginger leaf
        # ----------------------------------------------------

        leaf, bbox = detect_leaf(
            frame
        )

        # ----------------------------------------------------
        # Result panel
        # ----------------------------------------------------

        panel_width = 520

        panel = np.zeros(
            (
                frame.shape[0],
                panel_width,
                3
            ),
            dtype=np.uint8
        )

        # ====================================================
        # NO LEAF
        # ====================================================

        if leaf is None:

            if language == "kn":

                draw_unicode_text(
                    panel,
                    "ಶುಂಠಿ ಎಲೆ ರೋಗ ಪತ್ತೆ AI",
                    20,
                    15,
                    panel_width - 40,
                    55,
                    28,
                    (255, 255, 255)
                )

                draw_unicode_text(
                    panel,
                    "ಶುಂಠಿ ಎಲೆ ಪತ್ತೆಯಾಗಿಲ್ಲ",
                    20,
                    90,
                    panel_width - 40,
                    60,
                    26,
                    (0, 165, 255)
                )

                draw_unicode_text(
                    panel,
                    "ಕ್ಯಾಮೆರಾದ ಮುಂದೆ ಎಲೆಯನ್ನು ಇರಿಸಿ.",
                    20,
                    160,
                    panel_width - 40,
                    60,
                    20,
                    (220, 220, 220)
                )

            else:

                cv2.putText(
                    panel,
                    "GINGER LEAF DISEASE AI",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    panel,
                    "No ginger leaf detected",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 165, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    panel,
                    "Place a ginger leaf in front",
                    (20, 145),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (220, 220, 220),
                    1,
                    cv2.LINE_AA
                )

                cv2.putText(
                    panel,
                    "of the camera.",
                    (20, 175),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (220, 220, 220),
                    1,
                    cv2.LINE_AA
                )

            # Clear previous disease result.
            last_predictions = {}

            last_result_id = None

            last_result_probability = 0.0

            last_result_confirmed = False

        # ====================================================
        # LEAF DETECTED
        # ====================================================

        else:

            x1, y1, x2, y2 = bbox

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            if language == "kn":

                draw_unicode_text(
                    frame,
                    "ಶುಂಠಿ ಎಲೆ ಪತ್ತೆಯಾಗಿದೆ",
                    x1,
                    max(5, y1 - 45),
                    min(
                        400,
                        frame.shape[1] - x1
                    ),
                    40,
                    20,
                    (0, 255, 0)
                )

            else:

                cv2.putText(
                    frame,
                    "GINGER LEAF DETECTED",
                    (
                        x1,
                        max(
                            25,
                            y1 - 10
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

            # ------------------------------------------------
            # Run every available model
            # ------------------------------------------------

            if (
                frame_count
                % INFERENCE_EVERY_N_FRAMES
                == 0
            ):

                last_predictions = (
                    predict_all_models(
                        leaf
                    )
                )

                (
                    last_result_id,
                    last_result_probability,
                    last_result_confirmed
                ) = select_result(
                    last_predictions
                )

            # ------------------------------------------------
            # Draw result
            # ------------------------------------------------

            draw_result_panel(
                panel,
                last_result_id,
                last_result_probability,
                last_result_confirmed,
                language
            )

            # ------------------------------------------------
            # Draw all model probabilities
            # ------------------------------------------------

            draw_model_probabilities(
                panel,
                last_predictions,
                language
            )

        # ====================================================
        # LEFT SIDE
        # ====================================================

        if leaf is not None:

            crop_display = cv2.resize(
                leaf,
                (
                    frame.shape[1],
                    frame.shape[0]
                ),
                interpolation=cv2.INTER_AREA
            )

        else:

            crop_display = frame.copy()

        # ====================================================
        # COMBINE
        # ====================================================

        combined = np.hstack(
            (
                crop_display,
                panel
            )
        )

        # ====================================================
        # FPS
        # ====================================================

        current_time = time.time()

        elapsed = (
            current_time
            - previous_time
        )

        if elapsed > 0:

            fps = (
                1.0
                / elapsed
            )

        previous_time = (
            current_time
        )

        cv2.putText(
            combined,
            f"FPS: {fps:.1f}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

        # ====================================================
        # SHOW WINDOW
        # ====================================================

        cv2.imshow(
            "Ginger Leaf Disease Detection AI",
            combined
        )

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        if key == ord("q"):

            break

    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()