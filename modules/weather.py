"""
modules/weather.py
──────────────────
OpenWeatherMap integration:
  • Current weather (temp, humidity)
  • 5-day forecast → accumulated rainfall estimate
  • Geocoding by city name or lat/lon
"""

import requests
from modules.config import OPENWEATHER_API_KEY, OPENWEATHER_BASE


def get_weather_by_city(city: str) -> dict:
    """
    Fetch current weather + forecast for a city name.
    Returns a dict with: city, country, temp, humidity, rainfall_7d,
    weather_desc, wind_speed, pressure, feels_like, or error key.
    """
    try:
        # Current weather
        cur_url = f"{OPENWEATHER_BASE}/weather"
        cur_r   = requests.get(cur_url, params={
            "q":     city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }, timeout=8)

        if cur_r.status_code != 200:
            return {"error": f"City not found: {city}. Try a different spelling."}

        cur = cur_r.json()

        # 5-day / 3-hour forecast → sum rain
        fcst_url = f"{OPENWEATHER_BASE}/forecast"
        fcst_r   = requests.get(fcst_url, params={
            "q":     city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }, timeout=8)

        rainfall_5d = 0.0
        if fcst_r.status_code == 200:
            for item in fcst_r.json().get("list", []):
                rainfall_5d += item.get("rain", {}).get("3h", 0.0)

        return {
            "city":         cur.get("name", city),
            "country":      cur.get("sys", {}).get("country", ""),
            "temp":         round(cur["main"]["temp"], 1),
            "feels_like":   round(cur["main"]["feels_like"], 1),
            "humidity":     cur["main"]["humidity"],
            "pressure":     cur["main"]["pressure"],
            "wind_speed":   round(cur.get("wind", {}).get("speed", 0) * 3.6, 1),
            "weather_desc": cur["weather"][0]["description"].title(),
            "rainfall_7d":  round(rainfall_5d, 1),   # mm over next 5 days
            "lat":          cur["coord"]["lat"],
            "lon":          cur["coord"]["lon"],
        }

    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection. Enter weather values manually."}
    except Exception as e:
        return {"error": str(e)}


def get_weather_by_coords(lat: float, lon: float) -> dict:
    """Fetch weather by coordinates."""
    try:
        cur_r = requests.get(f"{OPENWEATHER_BASE}/weather", params={
            "lat": lat, "lon": lon,
            "appid": OPENWEATHER_API_KEY, "units": "metric",
        }, timeout=8)

        if cur_r.status_code != 200:
            return {"error": "Could not fetch weather for coordinates."}

        cur = cur_r.json()
        city = cur.get("name", f"{lat:.2f},{lon:.2f}")
        return get_weather_by_city(city)

    except Exception as e:
        return {"error": str(e)}


def weather_risk_summary(temp: float, humidity: float, rainfall: float) -> dict:
    """
    Compute drought and waterlogging risk indices.
    Returns: drought_risk (0-100), waterlog_risk (0-100), heat_stress (bool)
    """
    # Drought: low rainfall + low humidity + high temp
    drought = max(0, min(100,
        int((1 - min(rainfall, 200) / 200) * 50 +
            (1 - min(humidity, 100) / 100) * 30 +
            max(0, (temp - 30) / 15) * 20)
    ))

    # Waterlogging: high rainfall + high humidity
    waterlog = max(0, min(100,
        int(min(rainfall, 300) / 300 * 60 +
            min(humidity, 100) / 100 * 40)
    ))

    return {
        "drought_risk":  drought,
        "waterlog_risk": waterlog,
        "heat_stress":   temp > 38,
        "frost_risk":    temp < 5,
    }
