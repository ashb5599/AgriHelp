"""
modules/market.py
─────────────────
Live mandi (market) prices from data.gov.in API and Agmarknet fallback.

data.gov.in endpoint:  https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
  - requires api-key (free registration)
  - We include a curated fallback dataset so the app never crashes.
"""

import requests
from datetime import datetime

# ── data.gov.in API key (free — register at data.gov.in) ─────────────────────
DATA_GOV_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad38d07e3b63d7445"

# ── Curated fallback prices (₹/quintal) — updated Dec 2024 ───────────────────
FALLBACK_PRICES = {
    "rice":        {"price": 2183, "unit": "₹/quintal", "market": "Karnal, Haryana"},
    "wheat":       {"price": 2275, "unit": "₹/quintal", "market": "Hapur, UP"},
    "maize":       {"price": 2090, "unit": "₹/quintal", "market": "Davangere, Karnataka"},
    "chickpea":    {"price": 5400, "unit": "₹/quintal", "market": "Indore, MP"},
    "kidneybeans": {"price": 8500, "unit": "₹/quintal", "market": "Jammu"},
    "pigeonpeas":  {"price": 7000, "unit": "₹/quintal", "market": "Latur, Maharashtra"},
    "mothbeans":   {"price": 6200, "unit": "₹/quintal", "market": "Jodhpur, Rajasthan"},
    "mungbean":    {"price": 7500, "unit": "₹/quintal", "market": "Jaipur, Rajasthan"},
    "blackgram":   {"price": 6800, "unit": "₹/quintal", "market": "Nagpur, Maharashtra"},
    "lentil":      {"price": 6200, "unit": "₹/quintal", "market": "Bhopal, MP"},
    "pomegranate": {"price":12000, "unit": "₹/quintal", "market": "Solapur, Maharashtra"},
    "banana":      {"price": 2500, "unit": "₹/quintal", "market": "Jalgaon, Maharashtra"},
    "mango":       {"price": 5000, "unit": "₹/quintal", "market": "Ratnagiri, Maharashtra"},
    "grapes":      {"price": 7000, "unit": "₹/quintal", "market": "Nashik, Maharashtra"},
    "watermelon":  {"price": 1200, "unit": "₹/quintal", "market": "Hubli, Karnataka"},
    "muskmelon":   {"price": 1800, "unit": "₹/quintal", "market": "Pune, Maharashtra"},
    "apple":       {"price":12000, "unit": "₹/quintal", "market": "Shimla, HP"},
    "orange":      {"price": 4500, "unit": "₹/quintal", "market": "Nagpur, Maharashtra"},
    "papaya":      {"price": 1500, "unit": "₹/quintal", "market": "Coimbatore, TN"},
    "coconut":     {"price": 3200, "unit": "₹/quintal", "market": "Pollachi, TN"},
    "cotton":      {"price": 6620, "unit": "₹/quintal", "market": "Kurnool, AP"},
    "jute":        {"price": 5050, "unit": "₹/quintal", "market": "Kolkata, WB"},
    "coffee":      {"price":16000, "unit": "₹/quintal", "market": "Chikkamagaluru, Karnataka"},
    "groundnut":   {"price": 5440, "unit": "₹/quintal", "market": "Junagadh, Gujarat"},
    "barley":      {"price": 1635, "unit": "₹/quintal", "market": "Jaipur, Rajasthan"},
    "mustard":     {"price": 5650, "unit": "₹/quintal", "market": "Alwar, Rajasthan"},
}

# Simple seasonal multipliers to make prices feel dynamic
def _seasonal_multiplier() -> float:
    month = datetime.now().month
    # Prices typically higher in lean season (Apr-Jun), lower post-harvest
    seasonal = {1:1.02, 2:1.01, 3:1.00, 4:1.05, 5:1.07, 6:1.06,
                7:0.97, 8:0.96, 9:0.98, 10:0.99, 11:1.01, 12:1.03}
    return seasonal.get(month, 1.0)


def get_market_price(crop: str) -> dict:
    """
    Try data.gov.in API first; fall back to curated dataset.
    Returns dict with: crop, price, unit, market, trend, source
    """
    crop_lower = crop.lower().strip()

    # ── Try live API ─────────────────────────────────────────────────────────
    try:
        # Map our crop names to commodity names used in Agmarknet
        commodity_map = {
            "rice": "Rice", "wheat": "Wheat", "maize": "Maize",
            "cotton": "Cotton", "groundnut": "Groundnut",
            "chickpea": "Gram(Chick Pea)", "mustard": "Mustard",
            "banana": "Banana", "mango": "Mango", "coconut": "Coconut",
        }
        commodity = commodity_map.get(crop_lower)
        if commodity:
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            r = requests.get(url, params={
                "api-key": DATA_GOV_KEY,
                "format":  "json",
                "filters[commodity]": commodity,
                "limit":   5,
            }, timeout=6)

            if r.status_code == 200:
                records = r.json().get("records", [])
                if records:
                    rec   = records[0]
                    price = float(rec.get("modal_price", 0) or 0)
                    if price > 0:
                        return {
                            "crop":   crop,
                            "price":  int(price),
                            "unit":   "₹/quintal",
                            "market": f"{rec.get('market','—')}, {rec.get('state','—')}",
                            "date":   rec.get("arrival_date", "Today"),
                            "trend":  _price_trend(price, crop_lower),
                            "source": "data.gov.in (live)",
                        }
    except Exception:
        pass

    # ── Fallback ──────────────────────────────────────────────────────────────
    fb = FALLBACK_PRICES.get(crop_lower)
    if not fb:
        return {"crop": crop, "price": None, "error": "Price data not available"}

    mult  = _seasonal_multiplier()
    price = int(fb["price"] * mult)
    return {
        "crop":   crop,
        "price":  price,
        "unit":   fb["unit"],
        "market": fb["market"],
        "date":   "Reference (Dec 2024)",
        "trend":  _price_trend(price, crop_lower),
        "source": "Curated MSP / Agmarknet reference",
    }


def _price_trend(price: float, crop: str) -> str:
    """Simple trend indicator based on seasonal month."""
    mult = _seasonal_multiplier()
    if mult > 1.03:
        return "up"
    elif mult < 0.98:
        return "down"
    return "stable"


def get_profit_estimate(crop: str, land_acres: float = 1.0) -> dict:
    """
    Rough profit calculation per acre.
    Yield data (quintals/acre) is national average.
    """
    yields_qa = {  # quintals per acre
        "rice": 14, "wheat": 16, "maize": 18, "chickpea": 7,
        "cotton": 8, "groundnut": 10, "mustard": 10, "sugarcane": 350,
        "banana": 120, "mango": 50, "coconut": 60, "coffee": 5,
        "lentil": 6, "pigeonpeas": 7, "blackgram": 6, "mungbean": 5,
        "soybean": 10, "barley": 12, "grapes": 80, "papaya": 100,
    }
    costs_per_acre = {  # ₹ rough input cost
        "rice": 18000, "wheat": 15000, "maize": 14000, "chickpea": 12000,
        "cotton": 22000, "groundnut": 18000, "mustard": 12000,
    }

    price_data = get_market_price(crop)
    if not price_data.get("price"):
        return {}

    price   = price_data["price"]  # ₹/quintal
    yield_q = yields_qa.get(crop.lower(), 10) * land_acres
    revenue = price * yield_q
    cost    = costs_per_acre.get(crop.lower(), 15000) * land_acres
    profit  = revenue - cost

    return {
        "revenue":     int(revenue),
        "cost":        int(cost),
        "profit":      int(profit),
        "yield_q":     round(yield_q, 1),
        "price_per_q": price,
        "roi_pct":     round((profit / cost * 100) if cost else 0, 1),
    }
