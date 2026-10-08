# Architecture

Browser -> React frontend -> FastAPI -> image validation -> EfficientNetB0 -> disease database -> Google Translation (text only) -> English/Kannada result.

Laptop webcam: browser/OpenCV -> captured JPEG -> same `/api/predict` path.

ESP32-CAM: Wi-Fi HTTP/MJPEG stream -> laptop/server/OpenCV integration point -> CNN. CNN inference is not performed on ESP32-CAM.
