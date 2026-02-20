# TravelWAI Application Core (`app/`)

This directory contains the core business logic, the AI agent workflow, and external integrations for TravelWAI.

## Core Files

*   **`agent.py`**: A simple wrapper that exposes the compiled LangGraph workflow (`app_graph`) as `agent_executor` for use in the Streamlit frontend.
*   **`config.py`**: Centralized configuration management. It loads environment variables safely and manages API keys (Groq, SerpAPI, MongoDB) along with LLM model selection logic.
*   **`database.py`**: Contains `MongoStore`, a class that communicates with the FastAPI backend (`server.py`) via a REST API to securely persist generated travel plans and their evaluation scores to MongoDB.
*   **`evaluator.py`**: Defines the `PlanEvaluator` class. It uses the large language model (as a travel critic) to assign a quality score and provide feedback on the generated itinerary based on the user's initial prompt.
*   **`graph.py`**: The heart of the application. It defines the stateful **LangGraph** workflow encompassing the three primary nodes:
    1.  **Trip Parser**: Extracts structured JSON from the user's prompt using the small model.
    2.  **Generators (Parallel)**: Concurrently generates a sightseeing skeleton and searches/filters dining options via tools.
    3.  **Synthesizer**: Uses the large model to fuse the structured data into the final Markdown itinerary narrative.

## Tools (`app/tools/`)

This subdirectory contains the external tools and API wrappers invoked by the agent to fetch real-world travel data.

*   **`places.py`**: Functions to interface with Google Maps via SerpAPI.
    *   `search_places`: Finds generalized locations like sights, restaurants based on dietary preferences (e.g., vegetarian).
    *   `alt_restaurant_tool`: Finds alternative dining options prioritizing low wait times.
    *   `indoor_places_tool`: Specifically seeks out museums, galleries, and malls—ideal for bad weather contingencies.
*   **`planner.py`**: A utility function (`planner_agent`) containing logic to parse location addresses and cluster them by neighborhood, grouped for better daily routing.
*   **`stays.py`**: Contains `get_hotels`, which queries Google Hotels via SerpAPI to find top-rated accommodations for given check-in/out dates.
*   **`transport.py`**: Transportation-focused tools.
    *   `get_flights`: Queries Google Flights via SerpAPI for outbound flight options.
    *   `get_trains`: A placeholder/mock tool representing a search for train schedules.
