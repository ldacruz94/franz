from .time import get_current_time
from .weather import get_weather
from .web import web_search
from .system import open_app
from .tv import tv_power, tv_volume
from .theme import change_theme

ALL_TOOLS = [
    get_current_time, 
    get_weather, 
    web_search, 
    open_app, 
    tv_power, 
    tv_volume, 
    change_theme
]
