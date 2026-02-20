# TravelWAI External Tools (`app/tools/`)

This directory houses the external tool integrations that the LangGraph AI agent uses to interact with the real world, primarily through SerpAPI wrappers.

## Tool Files

*   **`places.py`**: Interacts with the Google Maps API.
    *   `search_places`: The primary search tool for locations like sights, restaurants based on specific criteria (e.g., 'vegetarian').
    *   `alt_restaurant_tool`: Specially searches for restaurants prioritizing low wait times.
    *   `indoor_places_tool`: Specifically finds indoor attractions (museums, malls), mainly used as a fallback for bad weather.
*   **`planner.py`**: Contains a utility planner module.
    *   `planner_agent`: Clusters raw location strings by neighborhood to assist in creating more logical, proximity-based generated itineraries.
*   **`stays.py`**: Interacts with the Google Hotels API.
    *   `get_hotels`: Finds top-rated accommodations based on city location and strict check-in/check-out dates.
*   **`transport.py`**: Handles external queries related to travel.
    *   `get_flights`: Interacts with Google Flights to find the best outbound options based on origin, destination, and departure date.
    *   `get_trains`: A placeholder function to represent querying logic for train schedules (e.g., IRCTC in India).
