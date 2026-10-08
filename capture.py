"""Optional local USB/laptop webcam capture utility using OpenCV."""
import cv2
from pathlib import Path
out=Path('camera_capture.jpg')
cap=cv2.VideoCapture(0)
if not cap.isOpened(): raise SystemExit('Could not open webcam.')
print('Press SPACE to capture, ESC to exit.')
while True:
    ok,frame=cap.read()
    if not ok: break
    cv2.imshow('Ginger Leaf Camera',frame)
    key=cv2.waitKey(1)&0xFF
    if key==32: cv2.imwrite(str(out),frame); print('Saved',out); break
    if key==27: break
cap.release(); cv2.destroyAllWindows()
