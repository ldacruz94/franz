from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from .prompt import build_system_prompt
from .tools import ALL_TOOLS, apply_theme_fallback

MODEL = "llama3.2:3b"

_llm = ChatOllama(model=MODEL)
_agent = create_react_agent(_llm, ALL_TOOLS, prompt=build_system_prompt())


def chat(message: str) -> str:
    result = _agent.invoke({"messages": [HumanMessage(content=message)]})
    reply = result["messages"][-1].content
    apply_theme_fallback(message)
    return reply
