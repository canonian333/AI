# F:\Projects\AI_PRJCTS\TravelWAI\app\tools\__init__.py

# 1. Use absolute imports for maximum stability
from app.tools.transport import get_flights, get_trains
from app.tools.stays import get_hotels
from app.tools.places import search_places, alt_restaurant_tool, indoor_places_tool

# 2. Define __all__ to explicitly control the public API
# This prevents internal variables from being accidentally imported.
__all__ = [
    "get_flights",
    "get_trains",
    "get_hotels",
    "search_places",
    "alt_restaurant_tool",
    "indoor_places_tool"
]