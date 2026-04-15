"""
modules/disease.py
──────────────────
Plant disease detection.

Two-tier approach:
  1. If TensorFlow is available + model weights exist → CNN inference
  2. Always-available colour heuristic (never crashes)

The colour heuristic analyses:
  • Yellow ratio  → nitrogen deficiency / fungal yellowing
  • Brown ratio   → blight / rot / necrosis
  • Dark spot ratio → fungal spots
  • Green health  → healthy index
"""

import io
import numpy as np
from PIL import Image
from modules.config import DISEASE_TREATMENTS

# Class names from PlantVillage dataset (38 classes)
CLASS_NAMES = list(DISEASE_TREATMENTS.keys())


# ── Colour heuristic ──────────────────────────────────────────────────────────
def _rgb_ratios(img_array: np.ndarray) -> dict:
    """Compute colour channel statistics from a resized RGB array."""
    r = img_array[:, :, 0].astype(float)
    g = img_array[:, :, 1].astype(float)
    b = img_array[:, :, 2].astype(float)

    total = r.size

    # Yellow: high R+G, low B
    yellow = np.sum((r > 160) & (g > 140) & (b < 100)) / total

    # Brown: high R, medium G, low B
    brown = np.sum((r > 120) & (g > 60) & (g < 130) & (b < 80)) / total

    # Dark spots: all channels low
    dark = np.sum((r < 60) & (g < 60) & (b < 60)) / total

    # Healthy green: G dominant
    green = np.sum((g > r) & (g > b) & (g > 80)) / total

    return {"yellow": yellow, "brown": brown, "dark": dark, "green": green}


def heuristic_diagnosis(img: Image.Image) -> dict:
    """
    Rule-based diagnosis from image colour profile.
    Returns: disease_name, confidence, treatment, method
    """
    img_small = img.resize((128, 128)).convert("RGB")
    arr = np.array(img_small)
    ratios = _rgb_ratios(arr)

    y, br, dk, gr = ratios["yellow"], ratios["brown"], ratios["dark"], ratios["green"]

    # Decision rules
    if gr > 0.45 and y < 0.05 and br < 0.05:
        disease = "Tomato___healthy"
        conf    = min(95, int(gr * 100) + 30)
    elif br > 0.20 and dk > 0.05:
        disease = "Tomato___Late_blight"
        conf    = int(min(88, br * 200))
    elif br > 0.12:
        disease = "Tomato___Early_blight"
        conf    = int(min(82, br * 180))
    elif y > 0.18:
        disease = "Corn_(maize)___Common_rust_"
        conf    = int(min(80, y * 160))
    elif y > 0.10:
        disease = "Tomato___Tomato_Yellow_Leaf_Curl_Virus"
        conf    = int(min(75, y * 150))
    elif dk > 0.08:
        disease = "Apple___Black_rot"
        conf    = int(min(78, dk * 300))
    else:
        disease = "Tomato___healthy"
        conf    = 60

    treatment = DISEASE_TREATMENTS.get(disease, "Consult a local agronomist.")
    plant, cond = _parse_class(disease)

    return {
        "disease":   disease,
        "plant":     plant,
        "condition": cond,
        "confidence": conf,
        "treatment": treatment,
        "method":    "Colour Analysis (CNN model not loaded)",
        "ratios":    ratios,
    }


def _parse_class(class_name: str) -> tuple:
    """Split 'Tomato___Late_blight' → ('Tomato', 'Late Blight')"""
    parts = class_name.split("___")
    plant = parts[0].replace("_", " ")
    cond  = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown"
    return plant, cond


# ── CNN inference (optional) ──────────────────────────────────────────────────
def cnn_predict(img: Image.Image, model_path: str = "plant_disease_model.h5") -> dict:
    """
    TensorFlow MobileNetV2 inference.
    Falls back to heuristic if TF not available or model not found.
    """
    import os
    if not os.path.exists(model_path):
        return heuristic_diagnosis(img)

    try:
        import tensorflow as tf
        IMG_SIZE = 224
        img_resized = img.resize((IMG_SIZE, IMG_SIZE)).convert("RGB")
        arr = np.array(img_resized, dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, 0)

        model = tf.keras.models.load_model(model_path)
        preds = model.predict(arr, verbose=0)[0]
        top_idx  = int(np.argmax(preds))
        disease  = CLASS_NAMES[top_idx] if top_idx < len(CLASS_NAMES) else "Unknown"
        conf     = int(preds[top_idx] * 100)
        plant, cond = _parse_class(disease)

        # Top 3
        top3_idx = np.argsort(preds)[::-1][:3]
        top3 = [(CLASS_NAMES[i], round(float(preds[i]) * 100, 1))
                for i in top3_idx if i < len(CLASS_NAMES)]

        return {
            "disease":    disease,
            "plant":      plant,
            "condition":  cond,
            "confidence": conf,
            "treatment":  DISEASE_TREATMENTS.get(disease, "Consult an agronomist."),
            "method":     "MobileNetV2 CNN",
            "top3":       top3,
        }
    except Exception:
        return heuristic_diagnosis(img)


def analyse_leaf(uploaded_file) -> dict:
    """Main entry point: accepts a Streamlit UploadedFile."""
    img = Image.open(io.BytesIO(uploaded_file.read())).convert("RGB")
    return cnn_predict(img)
