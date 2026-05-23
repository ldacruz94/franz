from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

SYSTEM_PROMPT = (
    "You are Franz, a sharp and concise personal AI assistant. "
    "Always address the user as 'sir'. "
    "Respond in 1-3 sentences unless the user asks for more detail. "
    "You have access to tools — use them whenever they help you answer accurately. "
    "IMPORTANT: When the user asks to change the color, theme, or appearance (e.g. 'change to red', "
    "'switch to blue', 'make it purple'), you MUST call the change_theme tool immediately."
)

MODEL = "llama3.2:3b"

_pending_theme: str | None = None


# ── Tools ─────────────────────────────────────────────────────────────────────

@tool
def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")


@tool
def web_search(query: str) -> str:
    """Search the web for current information, news, facts, or anything requiring up-to-date knowledge."""
    from ddgs import DDGS
    results = DDGS().text(query, max_results=4)
    if not results:
        return "No results found."
    return "\n\n".join(f"{r['title']}\n{r['body']}" for r in results)


@tool
def change_theme(color: str) -> str:
    """Change the Franz UI color theme.

    Available colors: blue, red, green, purple, orange, gold.
    Use this when the user asks to change the color, theme, or appearance.
    """
    global _pending_theme
    valid = {"blue", "red", "green", "purple", "orange", "gold"}
    color = color.lower().strip()

    if color not in valid:
        return f"Unknown theme '{color}'. Available: {', '.join(sorted(valid))}."
    _pending_theme = color

    return f"Theme changed to {color}."


def pop_theme() -> str | None:
    global _pending_theme
    theme, _pending_theme = _pending_theme, None
    return theme


_VALID_COLORS = {"blue", "red", "green", "purple", "orange", "gold"}
_CHANGE_INTENTS = {"change", "switch", "set", "make", "turn", "use", "apply", "go"}

def _color_fallback(message: str) -> None:
    """Apply theme directly if the model forgot to call the tool."""
    global _pending_theme
    if _pending_theme is not None:
        return
    words = set(message.lower().split())
    if words & _CHANGE_INTENTS:
        color = next((c for c in _VALID_COLORS if c in words), None)
        if color:
            _pending_theme = color


# ── Agent ─────────────────────────────────────────────────────────────────────

_llm = ChatOllama(model=MODEL)
_tools = [get_current_time, web_search, change_theme]
_agent = create_react_agent(_llm, _tools, prompt=SYSTEM_PROMPT)

_history: list = []


def chat(message: str) -> str:
    _history.append(HumanMessage(content=message))
    result = _agent.invoke({"messages": _history})
    
    # Last message is always the final text reply
    reply = result["messages"][-1].content
    _history.append(AIMessage(content=reply))
    _color_fallback(message)

    return reply
