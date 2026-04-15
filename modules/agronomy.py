"""
modules/agronomy.py
────────────────────
Agronomic helpers:
  • Field calendar generation (month-by-month)
  • Fertiliser dose calculator
  • Soil health scoring
  • Irrigation scheduling
"""

from modules.config import (
    KHARIF_CROPS, RABI_CROPS, PERENNIAL_CROPS, CROP_NPK, SOIL_ZONES
)

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

# Activity type → CSS-style colour (used in UI)
ACTIVITY_COLORS = {
    "Land Prep":   "#4A6275",
    "Sowing":      "#1B6CA8",
    "Irrigation":  "#0D9488",
    "Fertilising": "#7C5C1E",
    "Pest Mgmt":   "#B0281E",
    "Growing":     "#286A3A",
    "Harvest":     "#C8963E",
    "Rest":        "#D4DDE5",
    "Drying":      "#9A6318",
    "Storage":     "#4A6275",
}

# Kharif calendar (Jun–Nov)
_KHARIF = {
    "May": "Land Prep", "Jun": "Sowing", "Jul": "Growing",
    "Aug": "Irrigation", "Sep": "Fertilising", "Oct": "Pest Mgmt",
    "Nov": "Harvest", "Dec": "Drying", "Jan": "Storage",
    "Feb": "Rest", "Mar": "Rest", "Apr": "Land Prep",
}

# Rabi calendar (Oct–Mar)
_RABI = {
    "Sep": "Land Prep", "Oct": "Sowing", "Nov": "Growing",
    "Dec": "Irrigation", "Jan": "Fertilising", "Feb": "Pest Mgmt",
    "Mar": "Harvest", "Apr": "Drying", "May": "Storage",
    "Jun": "Rest", "Jul": "Rest", "Aug": "Land Prep",
}

# Perennial (year-round with seasonal peaks)
_PERENNIAL = {
    "Jan": "Irrigation", "Feb": "Fertilising", "Mar": "Growing",
    "Apr": "Pest Mgmt",  "May": "Growing",     "Jun": "Irrigation",
    "Jul": "Growing",    "Aug": "Irrigation",  "Sep": "Harvest",
    "Oct": "Harvest",    "Nov": "Harvest",      "Dec": "Rest",
}


def get_field_calendar(crop: str) -> dict:
    """
    Return month → activity mapping for a crop.
    Also returns key milestones list.
    """
    crop_l = crop.lower()
    if crop_l in KHARIF_CROPS:
        calendar = _KHARIF.copy()
        season   = "Kharif (Monsoon)"
        milestones = [
            ("Jun", "Sow seeds after first monsoon rain"),
            ("Sep", "Apply second dose of nitrogen fertiliser"),
            ("Nov", "Harvest when moisture content < 20%"),
        ]
    elif crop_l in RABI_CROPS:
        calendar = _RABI.copy()
        season   = "Rabi (Winter)"
        milestones = [
            ("Oct", "Sow after soil temperature drops below 25°C"),
            ("Jan", "Apply phosphorus top-dressing"),
            ("Mar", "Harvest when grain turns golden"),
        ]
    else:
        calendar = _PERENNIAL.copy()
        season   = "Perennial / Year-round"
        milestones = [
            ("Feb", "Apply organic manure before flowering"),
            ("Sep", "Harvest at peak ripeness"),
            ("Dec", "Pruning and orchard management"),
        ]

    return {
        "calendar":   calendar,
        "season":     season,
        "milestones": milestones,
        "colors":     ACTIVITY_COLORS,
    }


def fertiliser_recommendation(crop: str, N: float, P: float, K: float,
                               land_acres: float = 1.0) -> dict:
    """
    Calculate fertiliser doses to bridge the gap between
    current soil NPK and optimal NPK for the crop.

    Returns: dict with doses in kg/ha and product names.
    """
    crop_l  = crop.lower()
    opt_N, opt_P, opt_K = CROP_NPK.get(crop_l, (80, 40, 40))
    ha = land_acres * 0.405  # 1 acre = 0.405 ha

    deficit_N = max(0, opt_N - N)
    deficit_P = max(0, opt_P - P)
    deficit_K = max(0, opt_K - K)

    # Convert to product doses (approximate content):
    # Urea = 46% N, DAP = 18%N + 46%P₂O₅ (=20%P), MOP = 60%K₂O (=50%K)
    urea_kg  = round((deficit_N / 0.46) * ha, 1)
    dap_kg   = round((deficit_P / 0.20) * ha, 1)
    mop_kg   = round((deficit_K / 0.50) * ha, 1)

    schedule = []
    if urea_kg > 0:
        schedule.append({
            "product": "Urea (46% N)",
            "dose_kg": urea_kg,
            "timing": "Split: 50% at sowing, 50% at 30 days",
        })
    if dap_kg > 0:
        schedule.append({
            "product": "DAP (18N + 46P₂O₅)",
            "dose_kg": dap_kg,
            "timing": "Basal application at sowing",
        })
    if mop_kg > 0:
        schedule.append({
            "product": "MOP / Muriate of Potash (60% K₂O)",
            "dose_kg": mop_kg,
            "timing": "Basal application at sowing",
        })

    return {
        "optimal_N": opt_N, "optimal_P": opt_P, "optimal_K": opt_K,
        "deficit_N": round(deficit_N, 1),
        "deficit_P": round(deficit_P, 1),
        "deficit_K": round(deficit_K, 1),
        "schedule":  schedule,
        "land_ha":   round(ha, 2),
    }


def soil_health_score(N: float, P: float, K: float, ph: float,
                      humidity: float) -> dict:
    """
    Compute a 0-100 soil health score and individual ratings.
    """
    def rate(val, low, ideal_lo, ideal_hi, high):
        if val < low or val > high:
            return 0
        elif ideal_lo <= val <= ideal_hi:
            return 100
        elif val < ideal_lo:
            return int((val - low) / (ideal_lo - low) * 100)
        else:
            return int((high - val) / (high - ideal_hi) * 100)

    n_score  = rate(N,   0,  60,  120, 180)
    p_score  = rate(P,   0,  30,   80, 145)
    k_score  = rate(K,   0,  30,   80, 205)
    ph_score = rate(ph,  4,  6.0,  7.5, 9)
    hum_score= rate(humidity, 0, 40, 80, 100)

    composite = round((n_score*0.25 + p_score*0.20 + k_score*0.20 +
                       ph_score*0.25 + hum_score*0.10), 1)

    def label(s):
        return "Excellent" if s>=80 else "Good" if s>=60 else "Fair" if s>=40 else "Poor"

    return {
        "overall":   composite,
        "label":     label(composite),
        "N_score":   n_score,  "P_score": p_score,  "K_score": k_score,
        "ph_score":  ph_score, "hum_score": hum_score,
        "N_label":   label(n_score), "P_label": label(p_score),
        "K_label":   label(k_score), "ph_label": label(ph_score),
    }


def irrigation_advice(crop: str, rainfall: float, humidity: float,
                      temp: float) -> dict:
    """Simple irrigation frequency recommendation."""
    crop_l = crop.lower()
    # Water demand index
    water_demand = {"rice": 5, "sugarcane": 5, "banana": 4, "cotton": 3,
                    "wheat": 3, "maize": 3, "chickpea": 1, "mustard": 1}
    demand = water_demand.get(crop_l, 2)  # 1=low, 5=high

    effective_rain = rainfall * 0.7  # 70% efficiency
    et_daily = max(1, (temp - 10) * 0.15 + (100 - humidity) * 0.05)

    days_between = max(3, int(effective_rain / (et_daily * demand * 7)))
    days_between = min(days_between, 21)

    method = ("Flood / furrow" if crop_l in {"rice","sugarcane","banana"}
              else "Drip / sprinkler" if demand <= 2
              else "Sprinkler / furrow")

    return {
        "frequency_days": days_between,
        "method":         method,
        "demand_level":   ["—","Low","Low-Med","Medium","Med-High","High"][demand],
        "et_daily_mm":    round(et_daily, 1),
    }
