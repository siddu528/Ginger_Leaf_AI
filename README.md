# Ginger Leaf Disease Detection AI

A runnable academic project scaffold based on the supplied master specification. It contains a 20-disease knowledge database, FastAPI backend, React/Vite frontend, real-image EfficientNetB0 training/evaluation pipeline, photo upload, browser webcam capture, ESP32-CAM URL configuration, and Google Cloud Translation integration.

## Important scientific limitation
The 20 listed diseases are knowledge-base entries, not automatically 20 CNN classes. The repository intentionally contains no fake images and no pre-trained ginger model. Until real, verified images are added and a model is trained, `/api/predict` returns `model_not_ready` instead of a fabricated result.

## Project structure
```
Ginger_Leaf_AI/
├── backend/                 # FastAPI
├── frontend/                # React + Vite
├── config/diseases.json     # 20 disease knowledge records
├── dataset/                 # Empty labelled folders; add real images
├── models/                  # Trained .keras model goes here
├── train.py
├── evaluate.py
├── capture.py
├── requirements.txt
└── .env.example
```

## Windows setup
```cmd
cd /d "C:\path\to\Ginger_Leaf_AI"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### Backend
```cmd
cd backend
uvicorn app.main:app --reload
```
Backend: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

### Frontend
Open a second CMD:
```cmd
cd /d "C:\path\to\Ginger_Leaf_AI\frontend"
npm install
npm run dev
```
Then open the Vite URL shown in the terminal, normally http://localhost:5173.

## Google Kannada translation
Enable Cloud Translation in Google Cloud and configure credentials through environment variables. Never put credentials in React or Git.

```
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=C:\secure\service-account.json
```
If translation is unavailable, English results remain available and Kannada shows a temporary-unavailable message.

## Train the CNN
Add only real, correctly labelled ginger images to dataset folders. Then:
```cmd
python train.py
```
The script uses EfficientNetB0 transfer learning, 224x224 input, augmentation, early stopping, ReduceLROnPlateau and checkpointing. It saves `models/ginger_disease_model.keras` and `models/class_names.json`.

Do not claim an accuracy number until `evaluate.py` is run on an independent test dataset:
```cmd
python evaluate.py C:\path\to\independent_test_dataset
```

## Webcam
The web frontend uses the browser's camera permission for live capture. The optional `capture.py` uses OpenCV to capture a local USB webcam frame.

## ESP32-CAM
Set the stream URL in the frontend, e.g. `http://192.168.1.100:81/stream`. The CNN stays on the laptop/server. The ESP32-CAM is a remote camera source only.

## API
- GET `/api/health`
- GET `/api/diseases`
- GET `/api/diseases/{disease_id}`
- POST `/api/predict` (multipart image upload)
- POST `/api/translate`
- GET `/api/camera/status`
- POST `/api/camera/esp32`

## Safety/data policy
- No fake predictions or fake accuracy.
- No generated training images.
- No hard-coded API keys.
- No unverified pesticide recommendation is supplied.
- Verify current local crop-specific labels/advisories before using any chemical treatment.
- Leaf images cannot reliably establish diseases whose important symptoms occur in rhizomes, roots, soil, storage tissue or internal tissues.
