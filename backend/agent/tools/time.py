from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
