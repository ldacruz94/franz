import subprocess
from langchain_core.tools import tool

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


@tool
def open_app(name: str) -> str:
    """Open an application by name (e.g. 'chrome', 'spotify', 'vs code', 'discord')."""
    key = name.lower().strip()
    cmd = _APPS.get(key, ["cmd.exe", "/c", "start", name])

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {name}."
    except FileNotFoundError:
        return f"Could not launch '{name}'."
    except Exception as e:
        return f"Failed to open '{name}': {e}"
