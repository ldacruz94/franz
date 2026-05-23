from datetime import datetime

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

SYSTEM_PROMPT = (
    "You are Franz, a sharp and concise personal AI assistant. "
    "Always address the user as 'sir'. "
    "Respond in 1-3 sentences unless the user asks for more detail. "
    "You have access to tools — use them whenever they help you answer accurately. "

    "Use web_search when the user asks about latest, current, recent, news, prices, versions, documentation, "
    "software updates, comparisons, or anything that may have changed recently. "
    "When using web_search, answer only from the tool results. If results are weak, say so. "

    "IMPORTANT: When the user asks to change the color, theme, or appearance, "
    "you MUST call the change_theme tool immediately."
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
    """Search the web for current information. Use this for latest, recent, news, versions, prices, or uncertain facts."""
    from ddgs import DDGS

    search_queries = [
        query,
        f"{query} latest 2026",
        f"{query} official documentation"
    ]

    seen_urls = set()
    formatted_results = []

    with DDGS() as ddgs:
        for search_query in search_queries:
            results = ddgs.text(search_query, max_results=3)

            for r in results:
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                url = r.get("href", "").strip()

                if not title or not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                formatted_results.append(
                    f"Title: {title}\n"
                    f"URL: {url}\n"
                    f"Snippet: {body}"
                )

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

def chat(message: str) -> str:
    result = _agent.invoke({"messages": [HumanMessage(content=message)]})
    reply = result["messages"][-1].content
    _color_fallback(message)
    return reply
