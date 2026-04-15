"""
modules/config.py
─────────────────
Central configuration — API keys, constants, crop metadata.
"""

# ── API Keys ──────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = "ee4bd8b5fc7a49f2b231b25c073938d1"
OPENWEATHER_BASE    = "https://api.openweathermap.org/data/2.5"

# ── Data paths ────────────────────────────────────────────────────────────────
CROP_CSV = "Crop_recommendation.csv"  # place in project root

# ── Crop metadata ─────────────────────────────────────────────────────────────
# Season classification
KHARIF_CROPS     = {"rice","maize","cotton","jute","groundnut","pigeonpeas","mothbeans",
                    "mungbean","blackgram","kidneybeans"}
RABI_CROPS       = {"wheat","barley","lentil","chickpea","mustard"}
PERENNIAL_CROPS  = {"coconut","papaya","mango","banana","grapes","watermelon",
                    "muskmelon","apple","orange","pomegranate"}
ZAID_CROPS       = {"mungbean","watermelon","muskmelon"}

# NPK optimal ranges per crop (N, P, K in kg/ha)
CROP_NPK = {
    "rice":        (80,  40,  40),  "wheat":       (120, 60,  40),
    "maize":       (120, 60,  40),  "chickpea":    (20,  60,  20),
    "kidneybeans": (20,  60,  30),  "pigeonpeas":  (20,  50,  20),
    "mothbeans":   (20,  40,  20),  "mungbean":    (20,  40,  20),
    "blackgram":   (25,  50,  25),  "lentil":      (20,  40,  20),
    "pomegranate": (50,  25,  50),  "banana":      (200, 60, 200),
    "mango":       (100, 50,  50),  "grapes":      (50,  50,  50),
    "watermelon":  (80,  40,  60),  "muskmelon":   (80,  40,  50),
    "apple":       (70,  35,  70),  "orange":      (60,  30,  60),
    "papaya":      (60,  30,  50),  "coconut":     (50, 320,  200),
    "cotton":      (120, 60,  60),  "jute":        (60,  30,  30),
    "coffee":      (40,  40,  40),  "groundnut":   (25,  50,  75),
    "barley":      (90,  60,  40),  "mustard":     (80,  40,  40),
}

# Disease treatment database
DISEASE_TREATMENTS = {
    "Apple___Apple_scab":
        "Apply fungicide (captan or myclobutanil). Remove fallen leaves. Prune for air circulation.",
    "Apple___Black_rot":
        "Remove mummified fruit. Apply copper-based fungicide. Prune infected branches.",
    "Apple___Cedar_apple_rust":
        "Apply myclobutanil fungicide at bud break. Remove nearby cedar trees if possible.",
    "Apple___healthy": "No disease detected. Maintain regular monitoring.",
    "Blueberry___healthy": "No disease detected.",
    "Cherry_(including_sour)___Powdery_mildew":
        "Apply sulfur or potassium bicarbonate spray. Improve air circulation.",
    "Cherry_(including_sour)___healthy": "No disease detected.",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot":
        "Apply azoxystrobin fungicide. Rotate crops. Use resistant hybrids.",
    "Corn_(maize)___Common_rust_":
        "Apply propiconazole at early detection. Plant resistant varieties.",
    "Corn_(maize)___Northern_Leaf_Blight":
        "Apply fungicide at tasseling. Use resistant varieties. Crop rotation.",
    "Corn_(maize)___healthy": "No disease detected.",
    "Grape___Black_rot":
        "Apply mancozeb or myclobutanil. Remove infected berries. Prune for airflow.",
    "Grape___Esca_(Black_Measles)":
        "No chemical cure. Remove infected wood. Apply wound protectants after pruning.",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)":
        "Apply copper fungicide. Ensure good drainage. Remove infected leaves.",
    "Grape___healthy": "No disease detected.",
    "Orange___Haunglongbing_(Citrus_greening)":
        "No cure. Remove infected trees immediately. Control psyllid vector with imidacloprid.",
    "Peach___Bacterial_spot":
        "Apply copper bactericide. Avoid overhead irrigation. Use resistant varieties.",
    "Peach___healthy": "No disease detected.",
    "Pepper,_bell___Bacterial_spot":
        "Apply copper hydroxide spray. Use certified disease-free seed. Crop rotation.",
    "Pepper,_bell___healthy": "No disease detected.",
    "Potato___Early_blight":
        "Apply chlorothalonil or mancozeb. Remove lower infected leaves. Avoid overhead watering.",
    "Potato___Late_blight":
        "Apply metalaxyl immediately. Destroy infected plants. Do not compost infected material.",
    "Potato___healthy": "No disease detected.",
    "Raspberry___healthy": "No disease detected.",
    "Soybean___healthy": "No disease detected.",
    "Squash___Powdery_mildew":
        "Apply potassium bicarbonate or neem oil. Space plants for airflow.",
    "Strawberry___Leaf_scorch":
        "Apply captan fungicide. Remove infected leaves. Avoid wetting foliage.",
    "Strawberry___healthy": "No disease detected.",
    "Tomato___Bacterial_spot":
        "Apply copper bactericide every 7 days. Use drip irrigation. Rotate crops.",
    "Tomato___Early_blight":
        "Apply chlorothalonil. Remove lower leaves. Mulch to prevent soil splash.",
    "Tomato___Late_blight":
        "Apply mancozeb or copper fungicide immediately. Destroy infected plants.",
    "Tomato___Leaf_Miner":
        "Apply spinosad or abamectin. Remove heavily mined leaves.",
    "Tomato___Leaf_Mold":
        "Apply chlorothalonil. Reduce humidity. Increase plant spacing.",
    "Tomato___Septoria_leaf_spot":
        "Apply mancozeb or copper fungicide. Remove infected leaves. Avoid overhead watering.",
    "Tomato___Spider_mites Two-spotted_spider_mite":
        "Apply miticide or neem oil. Increase humidity. Introduce predatory mites.",
    "Tomato___Target_Spot":
        "Apply azoxystrobin fungicide. Remove infected material. Rotate crops.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus":
        "No chemical cure. Control whitefly vector. Remove infected plants.",
    "Tomato___Tomato_mosaic_virus":
        "No cure. Remove infected plants. Disinfect tools. Control aphids.",
    "Tomato___healthy": "No disease detected. Plant looks healthy.",
}

# Soil zone descriptions
SOIL_ZONES = {
    0: ("Sandy Loam Zone",  "Low water retention. Frequent irrigation needed. Good for root crops."),
    1: ("Clay-Rich Zone",   "High nutrient retention. Risk of waterlogging. Good for rice and wheat."),
    2: ("Balanced Loam",    "Ideal soil. Suitable for most crops. Excellent for vegetables."),
    3: ("Acidic Red Zone",  "Low pH. Needs lime application. Good for tea, coffee, rubber."),
    4: ("Saline Zone",      "High salt content. Use salt-tolerant crops. Leach with irrigation."),
    5: ("Nutrient-Rich Black Zone", "High organic matter. Excellent for cotton, soybean, and pulses."),
}
