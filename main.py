import os
import requests
import argparse
import datetime
from dotenv import load_dotenv

# ==============================
# CONFIGURATION
# ==============================
load_dotenv()  # reads .env in current folder

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ Missing OPENWEATHER_API_KEY in .env file")

BASE_URL = "https://api.openweathermap.org/data/2.5"

# ==============================
# CORE FUNCTIONS
# ==============================

def fetch_weather_current(city: str, units: str = "metric"):
    """Fetch current weather for a city."""
    url = f"{BASE_URL}/weather"
    params = {"q": city, "appid": API_KEY, "units": units}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}

    data = resp.json()
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})

    return {
        "city": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "temp": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "weather_main": weather.get("main"),
        "weather_desc": weather.get("description"),
        "wind_speed": wind.get("speed"),
    }


def fetch_weather_forecast(city: str, cnt: int = 5, units: str = "metric"):
    """Fetch 5-day/3-hour forecast (returns first `cnt` entries)."""
    url = f"{BASE_URL}/forecast"
    params = {"q": city, "appid": API_KEY, "units": units}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}

    data = resp.json()
    raw_list = data.get("list", [])
    forecasts = []

    for entry in raw_list[:cnt]:
        main = entry.get("main", {})
        weather = entry.get("weather", [{}])[0]
        wind = entry.get("wind", {})
        forecasts.append({
            "datetime": entry.get("dt_txt"),
            "temp": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "weather_main": weather.get("main"),
            "weather_desc": weather.get("description"),
            "wind_speed": wind.get("speed"),
        })

    return {
        "city": data.get("city", {}).get("name"),
        "country": data.get("city", {}).get("country"),
        "forecasts": forecasts,
    }

# ==============================
# DISPLAY HELPERS
# ==============================

def pretty_current(d):
    if "error" in d:
        return f"Error: {d['error']}"
    s = f"📍 {d['city']}, {d['country']}\n"
    s += f"🌤️  {d['weather_main']} - {d['weather_desc']}\n"
    s += f"🌡️  Temp: {d['temp']}°C (feels like {d['feels_like']}°C)\n"
    s += f"💧 Humidity: {d['humidity']}% | Pressure: {d['pressure']} hPa\n"
    s += f"💨 Wind speed: {d['wind_speed']} m/s\n"
    return s


def pretty_forecast(fc, show_n=5):
    if "error" in fc:
        return f"Error: {fc['error']}"
    out = []
    for entry in fc.get("forecasts", [])[:show_n]:
        dt_txt = entry.get("datetime")
        temp = entry.get("temp")
        desc = entry.get("weather_desc")
        out.append(f"{dt_txt}: {temp}°C, {desc}")
    return "\n".join(out) if out else "No forecast data."

# ==============================
# CLI MAIN
# ==============================

def main():
    parser = argparse.ArgumentParser(description="🌦️ Command-line Weather App")
    parser.add_argument("city", help="City name (e.g. Karachi or London,UK)")
    parser.add_argument("--forecast", action="store_true", help="Show forecast (next 5 entries)")
    parser.add_argument("--entries", type=int, default=5, help="Number of forecast entries to show")
    args = parser.parse_args()

    try:
        current = fetch_weather_current(args.city)
        print(pretty_current(current))

        if args.forecast:
            print("\n🔮 Forecast:")
            forecast = fetch_weather_forecast(args.city, cnt=args.entries)
            print(pretty_forecast(forecast, args.entries))

    except Exception as e:
        print("Unexpected error:", e)


if __name__ == "__main__":
    main()
