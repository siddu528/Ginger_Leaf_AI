import React, { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = "https://ginger-leaf-ai.onrender.com/api";
const LIVE_INTERVAL_MS = 1500;

const CLASS_DETAILS = {
  Healthy_Ginger: {
    cause: "No visible disease symptoms were identified by the current CNN class.",
    symptoms: "Leaf appears healthy with no strong visible disease pattern.",
    treatment: "Continue normal crop monitoring and maintain good field hygiene.",
    pesticide: "No pesticide recommendation for a healthy prediction."
  },

  Leaf_Blight: {
    cause: "Likely fungal leaf-blight symptoms.",
    symptoms:
      "Brown or yellowish leaf lesions, drying areas, and progressive damage may be visible.",
    treatment:
      "Remove severely affected leaves, improve field sanitation, and avoid prolonged leaf wetness.",
    pesticide:
      "Use only a locally approved fungicide according to the agricultural officer/product label."
  },

  Dehydrated: {
    cause: "The leaf appears to show water-stress or dehydration symptoms.",
    symptoms:
      "Leaf curling, drooping, dryness, or loss of normal green appearance may occur.",
    treatment:
      "Check soil moisture and irrigation. Avoid both prolonged drought and waterlogging.",
    pesticide:
      "Pesticide is normally not required for dehydration itself."
  },

  Pest_Damage: {
    cause: "The image shows a pattern associated with possible pest damage.",
    symptoms:
      "Chewed areas, holes, scraping, discoloration, or other feeding damage may be visible.",
    treatment:
      "Inspect the crop for insects and eggs and use integrated pest-management practices.",
    pesticide:
      "Use only an officially recommended insecticide after confirming the pest."
  }
};

function prettyName(value) {
  if (!value) return "Unknown";

  return String(value)
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


async function translateToKannada(text) {
  if (!text) return "";

  try {
    const response = await fetch(
      `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=kn&dt=t&q=${encodeURIComponent(text)}`
    );

    if (!response.ok) {
      throw new Error("Online translation failed");
    }

    const data = await response.json();

    if (Array.isArray(data) && Array.isArray(data[0])) {
      return data[0]
        .map((item) => item?.[0] || "")
        .join("");
    }

    return text;
  } catch (error) {
    console.error(
      "Kannada translation error:",
      error
    );

    return text;
  }
}

function extractPrediction(data) {
  const prediction =
    data?.prediction ||
    data?.result ||
    data?.data ||
    data;

  const condition =
    prediction?.condition ||
    prediction?.disease ||
    prediction?.class_name ||
    prediction?.class ||
    prediction?.label ||
    prediction?.predicted_class ||
    prediction?.model_class ||
    prediction?.prediction ||
    "Unknown";

  const confidence =
    prediction?.confidence ??
    prediction?.confidence_score ??
    prediction?.probability ??
    prediction?.score ??
    0;

  return {
    condition,
    confidence,
    translation:
      prediction?.translation ||
      data?.translation ||
      null,
    raw: data
  };
}
async function predictBlob(blob) {
  const formData = new FormData();

  formData.append(
    "file",
    blob,
    `ginger_camera_${Date.now()}.jpg`
  );

  const response = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    body: formData
  });

  const text = await response.text();

  let data;

  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Prediction failed with status ${response.status}.`
    );
  }

  return extractPrediction(data);
}

function ResultCard({ result, source }) {
  if (!result) {
    return (
      <div className="result-empty">
        <div className="result-empty-icon">🔍</div>
        <h3>No prediction yet</h3>
        <p>
          Upload a ginger leaf image or start the live camera AI detection.
        </p>
      </div>
    );
  }

  const conditionKey = result.condition;
  const details =
    CLASS_DETAILS[conditionKey] || {
      cause: "No additional information is available for this CNN class.",
      symptoms: "Refer to the original image and prediction.",
      treatment: "Consult an agricultural expert for confirmation.",
      pesticide: "Do not apply pesticide without confirming the disease or pest."
    };

  let confidenceNumber = Number(result.confidence);

  if (!Number.isFinite(confidenceNumber)) {
    confidenceNumber = 0;
  }

  if (confidenceNumber <= 1) {
    confidenceNumber *= 100;
  }

  confidenceNumber = Math.max(
    0,
    Math.min(100, confidenceNumber)
  );

  return (
    <div className="result-card">
      <div className="result-header">
        <div>
          <span className="result-source">{source}</span>

          <h2>{prettyName(conditionKey)}</h2>
        </div>

        <div className="confidence">
          {confidenceNumber.toFixed(1)}%
        </div>
      </div>

      <div className="confidence-bar">
        <div
          className="confidence-fill"
          style={{ width: `${confidenceNumber}%` }}
        />
      </div>

      <div className="result-grid">
        <div className="info-box">
          <h4>Cause / Reason</h4>
          <p>{details.cause}</p>
        </div>

        <div className="info-box">
          <h4>Symptoms</h4>
          <p>{details.symptoms}</p>
        </div>

        <div className="info-box">
          <h4>Treatment</h4>
          <p>{details.treatment}</p>
        </div>

        <div className="info-box">
          <h4>Pesticide</h4>
          <p>{details.pesticide}</p>
        </div>
      </div>

      <div className="result-footer">
        <strong>Detected:</strong>{" "}
        {new Date().toLocaleString()}
      </div>

      <div className="kannada-box">
  <h4>ಕನ್ನಡ ಮಾಹಿತಿ</h4>

  {result.translation ? (
    <>
      <div className="info-box">
        <h4>ರೋಗ</h4>
        <p>
          {result.translation.disease_name || "—"}
        </p>
      </div>

      <div className="info-box">
        <h4>ಕಾರಣ</h4>
        <p>
          {result.translation.reason || "—"}
        </p>
      </div>

      <div className="info-box">
        <h4>ಲಕ್ಷಣಗಳು</h4>
        <p>
          {result.translation.symptoms || "—"}
        </p>
      </div>

      <div className="info-box">
        <h4>ಚಿಕಿತ್ಸೆ</h4>
        <p>
          {result.translation.treatment || "—"}
        </p>
      </div>

      <div className="info-box">
        <h4>ಕೀಟನಾಶಕ / ಸಲಹೆ</h4>
        <p>
          {result.translation.pesticide || "—"}
        </p>
      </div>
    </>
  ) : (
    <p>
      ಕನ್ನಡ ಅನುವಾದ ಲಭ್ಯವಿಲ್ಲ.
    </p>
  )}
</div>
    </div>
  );
}

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const busyRef = useRef(false);
  const mountedRef = useRef(true);

  const [activeTab, setActiveTab] = useState("photo");

  const [photoPreview, setPhotoPreview] = useState("");
  const [photoFile, setPhotoFile] = useState(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [liveOn, setLiveOn] = useState(false);

  const [cameraError, setCameraError] = useState("");
  const [cameraMessage, setCameraMessage] = useState(
    "Camera is not started."
  );

  const [status, setStatus] = useState("Ready");

  const [result, setResult] = useState(null);
  const [resultSource, setResultSource] = useState("");

  const [espUrl, setEspUrl] = useState(
    () => localStorage.getItem("gingerEsp32Url") || ""
  );

  const [espConnected, setEspConnected] = useState(false);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;

      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => {
          track.stop();
        });
      }
    };
  }, []);

  const stopLiveProcessing = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    busyRef.current = false;

    if (mountedRef.current) {
      setLiveOn(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    stopLiveProcessing();

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }

    if (mountedRef.current) {
      setCameraOn(false);
      setCameraMessage("Camera is stopped.");
    }
  }, [stopLiveProcessing]);

  async function startCamera() {
    setCameraError("");
    setCameraMessage("Requesting camera access…");

    if (
      !navigator.mediaDevices ||
      !navigator.mediaDevices.getUserMedia
    ) {
      setCameraError(
        "This browser does not support webcam access. Use current Chrome or Edge."
      );
      return;
    }

    try {
      stopCamera();

      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            width: {
              ideal: 1280
            },
            height: {
              ideal: 720
            },
            facingMode: "user"
          },
          audio: false
        });

      streamRef.current = stream;

      if (!videoRef.current) {
        throw new Error(
          "Camera video element is not available."
        );
      }

      const video = videoRef.current;

      video.srcObject = stream;
      video.muted = true;
      video.autoplay = true;
      video.playsInline = true;

      await new Promise((resolve) => {
        if (video.readyState >= 2) {
          resolve();
          return;
        }

        const handleLoaded = () => {
          video.removeEventListener(
            "loadedmetadata",
            handleLoaded
          );
          resolve();
        };

        video.addEventListener(
          "loadedmetadata",
          handleLoaded
        );
      });

      await video.play();

      setCameraOn(true);

      setCameraMessage(
        "Camera is live. You should now see the camera image above."
      );

      setStatus("Camera connected");
    } catch (error) {
      console.error(error);

      if (streamRef.current) {
        streamRef.current
          .getTracks()
          .forEach((track) => track.stop());

        streamRef.current = null;
      }

      setCameraOn(false);

      let message = "Could not start the camera.";

      if (error?.name === "NotAllowedError") {
        message =
          "Camera permission was denied. Allow camera access in Chrome and try again.";
      } else if (error?.name === "NotFoundError") {
        message =
          "No camera was found. Check that your laptop/USB camera is connected.";
      } else if (error?.name === "NotReadableError") {
        message =
          "The camera is already being used by another application. Close Teams, Zoom, Camera app, etc.";
      } else if (error?.name === "OverconstrainedError") {
        message =
          "The selected camera settings are not supported. Try another camera.";
      } else if (error?.message) {
        message = error.message;
      }

      setCameraError(message);
      setCameraMessage("Camera failed to start.");
    }
  }

  async function processLiveFrame() {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    if (!streamRef.current) return;

    if (busyRef.current) return;

    if (
      video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA
    ) {
      return;
    }

    if (
      video.videoWidth <= 0 ||
      video.videoHeight <= 0
    ) {
      return;
    }

    busyRef.current = true;

    try {
      const width = video.videoWidth;
      const height = video.videoHeight;

      canvas.width = width;
      canvas.height = height;

      const context = canvas.getContext("2d");

      if (!context) {
        throw new Error("Could not create camera canvas.");
      }

      context.drawImage(
        video,
        0,
        0,
        width,
        height
      );

      const blob = await new Promise((resolve) => {
        canvas.toBlob(
          resolve,
          "image/jpeg",
          0.82
        );
      });

      if (!blob) {
        throw new Error(
          "Could not capture a frame from the camera."
        );
      }

      if (mountedRef.current) {
        setStatus("AI analyzing live frame…");
      }

      const prediction = await predictBlob(blob);

      if (mountedRef.current) {
        setResult(prediction);
        setResultSource("LIVE CNN");
        setStatus("Live prediction updated");
      }
    } catch (error) {
      console.error(error);

      if (mountedRef.current) {
        setStatus(
          `Live detection error: ${
            error?.message || "Unknown error"
          }`
        );
      }
    } finally {
      busyRef.current = false;
    }
  }

  function startLiveProcessing() {
    if (!cameraOn || !streamRef.current) {
      setCameraError(
        "Start the laptop/USB camera first."
      );
      return;
    }

    if (liveOn) return;

    setCameraError("");
    setLiveOn(true);
    setStatus("Live AI detection started");

    processLiveFrame();

    timerRef.current = setInterval(
      processLiveFrame,
      LIVE_INTERVAL_MS
    );
  }

  function handlePhotoChange(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    setPhotoFile(file);
    setResult(null);
    setResultSource("");

    const url = URL.createObjectURL(file);

    setPhotoPreview((oldUrl) => {
      if (oldUrl) {
        URL.revokeObjectURL(oldUrl);
      }

      return url;
    });
  }

  async function detectPhoto() {
    if (!photoFile) {
      setStatus("Please select a ginger leaf image first.");
      return;
    }

    try {
      setStatus("Analyzing uploaded image…");

      const prediction = await predictBlob(
        photoFile
      );

      setResult(prediction);
      setResultSource("PHOTO CNN");
      setStatus("Photo prediction completed");
    } catch (error) {
      console.error(error);

      setStatus(
        `Photo detection error: ${
          error?.message || "Unknown error"
        }`
      );
    }
  }

  function connectEsp32() {
    const url = espUrl.trim();

    if (!url) {
      setStatus(
        "Enter the current ESP32-CAM stream URL."
      );
      return;
    }

    try {
      new URL(url);
    } catch {
      setStatus(
        "Enter a valid URL such as http://192.168.1.100:81/stream"
      );
      return;
    }

    localStorage.setItem(
      "gingerEsp32Url",
      url
    );

    setEspConnected(true);
    setStatus("ESP32-CAM stream connected.");
  }

  function disconnectEsp32() {
    setEspConnected(false);
    setStatus("ESP32-CAM disconnected.");
  }

  return (
    <div className="app">
      <header className="top-header">
        <div>
          <h1>🌱 Ginger Leaf AI</h1>
          <p>
            Ginger Leaf Disease Detection System
          </p>
        </div>

        <div className="backend-status">
          <span className="status-dot" />
          Backend: 127.0.0.1:8000
        </div>
      </header>

      <main className="container">
        <div className="tabs">
          <button
            className={
              activeTab === "photo"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("photo")}
          >
            📷 Photo Detection
          </button>

          <button
            className={
              activeTab === "camera"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("camera")}
          >
            🎥 Live Camera
          </button>

          <button
            className={
              activeTab === "esp32"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("esp32")}
          >
            📡 ESP32-CAM
          </button>
        </div>

        {activeTab === "photo" && (
          <section className="panel">
            <div className="panel-heading">
              <h2>Photo Detection</h2>
              <p>
                Upload a ginger leaf image and run the
                trained CNN.
              </p>
            </div>

            <div className="upload-area">
              <input
                id="leaf-file"
                type="file"
                accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
                onChange={handlePhotoChange}
              />

              <label
                htmlFor="leaf-file"
                className="upload-button"
              >
                Choose Leaf Image
              </label>

              {photoPreview && (
                <div className="photo-preview">
                  <img
                    src={photoPreview}
                    alt="Selected ginger leaf"
                  />
                </div>
              )}

              <button
                className="primary-button"
                onClick={detectPhoto}
                disabled={!photoFile}
              >
                🔎 Detect Disease
              </button>
            </div>
          </section>
        )}

        {activeTab === "camera" && (
          <section className="panel">
            <div className="panel-heading">
              <h2>Live Laptop / USB Camera</h2>
              <p>
                Start the camera first. The live video
                will appear inside this page.
              </p>
            </div>

            <div className="camera-stage">
              {!cameraOn && (
                <div className="camera-placeholder">
                  <div className="camera-icon">
                    🎥
                  </div>

                  <h3>Camera is not running</h3>

                  <p>
                    Click <strong>Start Camera</strong>
                    to show your laptop or USB camera.
                  </p>
                </div>
              )}

              <video
                ref={videoRef}
                className={
                  cameraOn
                    ? "camera-video visible"
                    : "camera-video"
                }
                autoPlay
                muted
                playsInline
              />

              <canvas
                ref={canvasRef}
                className="hidden-canvas"
              />

              {cameraOn && (
                <div className="camera-live-badge">
                  ● LIVE CAMERA
                </div>
              )}
            </div>

            <div className="camera-controls">
              <button
                className="primary-button"
                onClick={startCamera}
                disabled={cameraOn}
              >
                🎥 Start Camera
              </button>

              <button
                className="secondary-button"
                onClick={startLiveProcessing}
                disabled={!cameraOn || liveOn}
              >
                🤖 Start Live AI Detection
              </button>

              <button
                className="warning-button"
                onClick={stopLiveProcessing}
                disabled={!liveOn}
              >
                ⏸ Stop AI Detection
              </button>

              <button
                className="danger-button"
                onClick={stopCamera}
                disabled={!cameraOn}
              >
                ⏹ Stop Camera
              </button>
            </div>

            <div className="camera-message">
              <strong>Status:</strong>{" "}
              {cameraMessage}
            </div>

            {cameraError && (
              <div className="error-box">
                <strong>Camera Error:</strong>{" "}
                {cameraError}
              </div>
            )}

            <div className="live-info">
              <h3>How Live AI Detection Works</h3>

              <ol>
                <li>
                  Start Camera.
                </li>

                <li>
                  The real laptop/USB camera video
                  appears above.
                </li>

                <li>
                  Click Start Live AI Detection.
                </li>

                <li>
                  The browser captures a frame about
                  every 1.5 seconds.
                </li>

                <li>
                  Each frame is sent to the existing
                  <code>/api/predict</code> endpoint.
                </li>

                <li>
                  The CNN prediction is updated
                  continuously.
                </li>
              </ol>
            </div>
          </section>
        )}

        {activeTab === "esp32" && (
          <section className="panel">
            <div className="panel-heading">
              <h2>ESP32-CAM</h2>

              <p>
                Enter the current ESP32-CAM stream URL.
                The IP can change whenever your router
                assigns a new DHCP address.
              </p>
            </div>

            <div className="esp-controls">
              <input
                type="text"
                value={espUrl}
                onChange={(event) =>
                  setEspUrl(event.target.value)
                }
                placeholder="http://192.168.1.100:81/stream"
              />

              <button
                className="primary-button"
                onClick={connectEsp32}
              >
                Connect
              </button>

              <button
                className="danger-button"
                onClick={disconnectEsp32}
                disabled={!espConnected}
              >
                Disconnect
              </button>
            </div>

            {espConnected && espUrl && (
              <div className="esp-stream">
                <div className="stream-header">
                  <span>
                    ● ESP32-CAM LIVE STREAM
                  </span>

                  <small>{espUrl}</small>
                </div>

                <img
                  src={espUrl}
                  alt="ESP32-CAM live stream"
                  onError={() =>
                    setStatus(
                      "ESP32-CAM stream could not be loaded. Check the URL and Wi-Fi connection."
                    )
                  }
                />
              </div>
            )}

            {!espConnected && (
              <div className="esp-placeholder">
                <div className="camera-icon">
                  📡
                </div>

                <h3>ESP32-CAM not connected</h3>

                <p>
                  Example:
                </p>

                <code>
                  http://192.168.1.100:81/stream 
                </code> 
              </div> 
            )} 
 
            <div className="live-info"> 
              <h3>ESP32-CAM Important Note</h3> 
 
              <p> 
                The ESP32-CAM URL is not hard-coded. 
                Enter the current URL whenever the DHCP 
                address changes. 
              </p> 
 
              <p> 
                The browser can display the ESP32 stream, 
                but browser security/CORS restrictions 
                can prevent direct frame extraction for 
                CNN prediction. Do not treat the stream 
                as an AI prediction unless the frame has 
                actually been sent through the backend 
                prediction API. 
              </p> 
            </div> 
          </section> 
        )} 
 
        <section className="status-panel"> 
          <strong>System Status</strong> 
 
          <span>{status}</span> 
        </section> 
 
        <section className="result-section"> 
          <div className="panel-heading"> 
            <h2>Detection Result</h2> 
 
            <p> 
              Current CNN classes: 
              {" "} 
              Healthy_Ginger, Leaf_Blight, 
              Dehydrated, Pest_Damage 
            </p> 
          </div> 
 
          <ResultCard 
            result={result} 
            source={resultSource} 
          /> 
        </section> 
      </main> 
 
      <footer> 
        <p> 
          Ginger Leaf AI • SIH 2026 Project 
        </p> 
      </footer> 
    </div> 
  ); 
} 
