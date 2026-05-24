import json
import urllib.request
from langchain_core.tools import tool

_WMO = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


@tool
def get_weather() -> str:
    """Get the current weather for the user's location (Milford, MA)."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=42.1401&longitude=-71.5128"
        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
        "wind_speed_10m,precipitation,weather_code"
        "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
    )

    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read())

    c = data["current"]
    condition = _WMO.get(c["weather_code"], f"Code {c['weather_code']}")

    return (
        f"Milford, MA — {condition}\n"
        f"Temperature: {c['temperature_2m']}°F (feels like {c['apparent_temperature']}°F)\n"
        f"Humidity: {c['relative_humidity_2m']}%\n"
        f"Wind: {c['wind_speed_10m']} mph\n"
        f"Precipitation: {c['precipitation']} in"
    )
