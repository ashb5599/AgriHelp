"""
modules/disease.py
──────────────────
Plant disease detection system (YOLO + CNN + Heuristic fallback)
"""

import io
import os
import numpy as np
from PIL import Image
from ultralytics import YOLO
from modules.config import DISEASE_TREATMENTS

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
YOLO_MODEL_PATH = "runs/detect/plant_disease3/weights/best.pt"
CNN_MODEL_PATH  = "plant_disease_model.h5"

# Load YOLO once
_yolo_model = None
if os.path.exists(YOLO_MODEL_PATH):
    try:
        _yolo_model = YOLO(YOLO_MODEL_PATH)
    except:
        _yolo_model = None

# Load CNN once (lazy loading)
_cnn_model = None

# Class names
CLASS_NAMES = list(DISEASE_TREATMENTS.keys())


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def _parse_class(class_name: str) -> tuple:
    """Split 'Tomato___Late_blight' → ('Tomato', 'Late Blight')"""
    parts = class_name.split("___")
    plant = parts[0].replace("_", " ")
    cond  = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown"
    return plant, cond


# ─────────────────────────────────────────────────────────────
# YOLO PREDICTION (BEST)
# ─────────────────────────────────────────────────────────────
def yolo_predict(img: Image.Image) -> dict | None:
    if _yolo_model is None:
        return None

    try:
        results = _yolo_model.predict(img, conf=0.4)

        detections = []
        for r in results:
            for box in r.boxes:
                label = _yolo_model.names[int(box.cls)]
                conf  = float(box.conf)
                detections.append((label, conf))

        if not detections:
            return None

        label, conf = max(detections, key=lambda x: x[1])

        # Format label
        if "___" in label:
            plant, cond = _parse_class(label)
        elif "_" in label:
            parts = label.split("_", 1)
            plant = parts[0]
            cond  = parts[1].replace("_", " ").title()
        else:
            plant, cond = "Unknown", label

        return {
            "disease": label,
            "plant": plant,
            "condition": cond,
            "confidence": int(conf * 100),
            "treatment": DISEASE_TREATMENTS.get(
                label, "Apply fungicide and remove infected parts."
            ),
            "method": "YOLOv8 Detection",
        }

    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# CNN PREDICTION
# ─────────────────────────────────────────────────────────────
def cnn_predict(img: Image.Image) -> dict:
    global _cnn_model

    if not os.path.exists(CNN_MODEL_PATH):
        return heuristic_diagnosis(img)

    try:
        import tensorflow as tf

        # Load model only once
        if _cnn_model is None:
            _cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)

        model = _cnn_model

        IMG_SIZE = 224
        img_resized = img.resize((IMG_SIZE, IMG_SIZE)).convert("RGB")
        arr = np.array(img_resized, dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, 0)

        preds = model.predict(arr, verbose=0)[0]
        top_idx = int(np.argmax(preds))

        disease = CLASS_NAMES[top_idx] if top_idx < len(CLASS_NAMES) else "Unknown"
        conf = int(preds[top_idx] * 100)

        plant, cond = _parse_class(disease)

        top3_idx = np.argsort(preds)[::-1][:3]
        top3 = [
            (CLASS_NAMES[i], round(float(preds[i]) * 100, 1))
            for i in top3_idx if i < len(CLASS_NAMES)
        ]

        return {
            "disease": disease,
            "plant": plant,
            "condition": cond,
            "confidence": conf,
            "treatment": DISEASE_TREATMENTS.get(
                disease, "Consult an agronomist."
            ),
            "method": "MobileNetV2 CNN",
            "top3": top3,
        }

    except Exception:
        return heuristic_diagnosis(img)


# ─────────────────────────────────────────────────────────────
# HEURISTIC (ALWAYS WORKS)
# ─────────────────────────────────────────────────────────────
def _rgb_ratios(img_array: np.ndarray) -> dict:
    r = img_array[:, :, 0].astype(float)
    g = img_array[:, :, 1].astype(float)
    b = img_array[:, :, 2].astype(float)

    total = r.size

    yellow = np.sum((r > 160) & (g > 140) & (b < 100)) / total
    brown  = np.sum((r > 120) & (g > 60) & (g < 130) & (b < 80)) / total
    dark   = np.sum((r < 60) & (g < 60) & (b < 60)) / total
    green  = np.sum((g > r) & (g > b) & (g > 80)) / total

    return {"yellow": yellow, "brown": brown, "dark": dark, "green": green}


def heuristic_diagnosis(img: Image.Image) -> dict:
    img_small = img.resize((128, 128)).convert("RGB")
    arr = np.array(img_small)
    ratios = _rgb_ratios(arr)

    y, br, dk, gr = ratios["yellow"], ratios["brown"], ratios["dark"], ratios["green"]

    if gr > 0.45 and y < 0.05 and br < 0.05:
        disease = "Tomato___healthy"
        conf = min(95, int(gr * 100) + 30)
    elif br > 0.20 and dk > 0.05:
        disease = "Tomato___Late_blight"
        conf = int(min(88, br * 200))
    elif br > 0.12:
        disease = "Tomato___Early_blight"
        conf = int(min(82, br * 180))
    elif y > 0.18:
        disease = "Corn_(maize)___Common_rust_"
        conf = int(min(80, y * 160))
    elif y > 0.10:
        disease = "Tomato___Tomato_Yellow_Leaf_Curl_Virus"
        conf = int(min(75, y * 150))
    elif dk > 0.08:
        disease = "Apple___Black_rot"
        conf = int(min(78, dk * 300))
    else:
        disease = "Tomato___healthy"
        conf = 60

    plant, cond = _parse_class(disease)

    return {
        "disease": disease,
        "plant": plant,
        "condition": cond,
        "confidence": conf,
        "treatment": DISEASE_TREATMENTS.get(
            disease, "Consult a local agronomist."
        ),
        "method": "Colour Analysis (Fallback)",
        "ratios": ratios,
    }


# ─────────────────────────────────────────────────────────────
# MAIN ENTRY
# ─────────────────────────────────────────────────────────────
def analyse_leaf(uploaded_file) -> dict:
    uploaded_file.seek(0)
    img = Image.open(uploaded_file).convert("RGB")

    # 1️⃣ YOLO
    yolo_res = yolo_predict(img)
    if yolo_res:
        return yolo_res

    # 2️⃣ CNN 
    cnn_res = cnn_predict(img)
    if cnn_res:
        return cnn_res

    # 3️⃣ Heuristic fallback
    return heuristic_diagnosis(img)
