from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

SYSTEM_PROMPT = (
    "You are Franz, a sharp and concise personal AI assistant. "
    "Always address the user as 'sir'. "
    "Respond in 1-3 sentences unless the user asks for more detail. "
    "You have access to tools — use them whenever they help you answer accurately."
)

MODEL = "llama3.2:3b"

_pending_theme: str | None = None


# ── Tools ─────────────────────────────────────────────────────────────────────

@tool
def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")


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


# ── Agent ─────────────────────────────────────────────────────────────────────

_llm = ChatOllama(model=MODEL)
_tools = [get_current_time, change_theme]
_agent = create_react_agent(_llm, _tools, prompt=SYSTEM_PROMPT)

_history: list = []


def chat(message: str) -> str:
    _history.append(HumanMessage(content=message))
    result = _agent.invoke({"messages": _history})
    
    # Last message is always the final text reply
    reply = result["messages"][-1].content
    _history.append(AIMessage(content=reply))

    return reply
