from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")


@tool
def get_weather() -> str:
    """Get the current weather for the user's location (Milford, MA)."""
    import json
    import urllib.request

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=42.1401&longitude=-71.5128"
        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
        "wind_speed_10m,precipitation,weather_code"
        "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
    )

    WMO = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }

    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read())

    c = data["current"]
    condition = WMO.get(c["weather_code"], f"Code {c['weather_code']}")

    return (
        f"Milford, MA — {condition}\n"
        f"Temperature: {c['temperature_2m']}°F (feels like {c['apparent_temperature']}°F)\n"
        f"Humidity: {c['relative_humidity_2m']}%\n"
        f"Wind: {c['wind_speed_10m']} mph\n"
        f"Precipitation: {c['precipitation']} in"
    )


@tool
def web_search(query: str) -> str:
    """Search the web for current information. Use this for latest, recent, news, versions, prices, or uncertain facts."""
    from ddgs import DDGS

    search_queries = [
        query,
        f"{query} latest 2026",
        f"{query} official documentation",
    ]

    seen_urls: set[str] = set()
    formatted_results: list[str] = []

    with DDGS() as ddgs:
        for search_query in search_queries:
            for r in ddgs.text(search_query, max_results=3):
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                url = r.get("href", "").strip()

                if not title or not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                formatted_results.append(f"Title: {title}\nURL: {url}\nSnippet: {body}")

                if len(formatted_results) >= 5:
                    break

            if len(formatted_results) >= 5:
                break

    if not formatted_results:
        return "No reliable search results found."

    return (
        "Use ONLY these search results to answer. "
        "If the results are weak or incomplete, say so.\n\n"
        + "\n\n---\n\n".join(formatted_results)
    )


@tool
def open_app(name: str) -> str:
    """Open an application by name (e.g. 'chrome', 'spotify', 'vs code', 'discord')."""
    import subprocess

    _APPS: dict[str, list[str]] = {
        # Browsers
        "chrome":               ["cmd.exe", "/c", "start", "chrome"],
        "google chrome":        ["cmd.exe", "/c", "start", "chrome"],
        "firefox":              ["cmd.exe", "/c", "start", "firefox"],
        "edge":                 ["cmd.exe", "/c", "start", "msedge"],
        "microsoft edge":       ["cmd.exe", "/c", "start", "msedge"],
        # Dev
        "vscode":               ["code"],
        "vs code":              ["code"],
        "visual studio code":   ["code"],
        # Media / social
        "spotify":              ["cmd.exe", "/c", "start", "spotify"],
        "discord":              ["cmd.exe", "/c", "start", "discord"],
        "steam":                ["cmd.exe", "/c", "start", "steam"],
        # System
        "explorer":             ["explorer.exe", "."],
        "file explorer":        ["explorer.exe", "."],
        "notepad":              ["notepad.exe"],
        "calculator":           ["calc.exe"],
        "task manager":         ["taskmgr.exe"],
        "terminal":             ["cmd.exe", "/c", "start", "wt"],
        "windows terminal":     ["cmd.exe", "/c", "start", "wt"],
    }

    key = name.lower().strip()
    # Fall back to letting Windows resolve the name itself
    cmd = _APPS.get(key, ["cmd.exe", "/c", "start", name])

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {name}."
    except FileNotFoundError:
        return f"Could not launch '{name}'."
    except Exception as e:
        return f"Failed to open '{name}': {e}"


# ── Theme state ───────────────────────────────────────────────────────────────

_VALID_COLORS = {"blue", "red", "green", "purple", "orange", "gold"}
_CHANGE_INTENTS = {"change", "switch", "set", "make", "turn", "use", "apply", "go"}

_pending_theme: str | None = None


@tool
def change_theme(color: str) -> str:
    """Change the Franz UI color theme.

    Available colors: blue, red, green, purple, orange, gold.
    Use this when the user asks to change the color, theme, or appearance.
    """
    global _pending_theme
    color = color.lower().strip()

    if color not in _VALID_COLORS:
        return f"Unknown theme '{color}'. Available: {', '.join(sorted(_VALID_COLORS))}."

    _pending_theme = color
    return f"Theme changed to {color}."


def pop_theme() -> str | None:
    global _pending_theme
    theme, _pending_theme = _pending_theme, None
    return theme


def apply_theme_fallback(message: str) -> None:
    """Apply theme directly if the model forgot to call the tool."""
    global _pending_theme
    if _pending_theme is not None:
        return
    words = set(message.lower().split())
    if words & _CHANGE_INTENTS:
        color = next((c for c in _VALID_COLORS if c in words), None)
        if color:
            _pending_theme = color


ALL_TOOLS = [get_current_time, get_weather, web_search, open_app, change_theme]
