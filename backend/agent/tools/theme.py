from langchain_core.tools import tool

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
