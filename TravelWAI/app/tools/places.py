from langchain.tools import tool
import requests
import json
from app.config import Config

@tool
def search_places(location: str, preference: str = "sights"):
    """
    Finds places based on preference. 
    Preference can be: 'vegetarian', 'non-vegetarian', 'sights', 'museums', 'beaches', 'taxi services', 'car rentals', etc.
    Useful for finding specific types of locations or services.
    """
    params = {
        "engine": "google_maps",
        "q": f"{preference} in {location}",
        "type": "search",
        "api_key": Config.SERPAPI_API_KEY
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        results = res.get("local_results", [])

        if not results:
            return f"No {preference} found in {location}."

        # Production Logic: Prioritize Rating and Review Count
        sorted_places = sorted(
            results, 
            key=lambda x: (x.get("rating", 0), x.get("reviews", 0)), 
            reverse=True
        )[:6]
        
        clean_data = []
        for p in sorted_places:
            clean_data.append({
                "title": p.get("title"),
                "rating": p.get("rating"),
                "address": p.get("address")
            })

        return json.dumps(clean_data) 
    except Exception as e:
        return f"Places Search Error: {str(e)}"

@tool
def alt_restaurant_tool(location: str):
    """
    Finds alternative dining options with lower wait times or quick service.
    """
    params = {
        "engine": "google_maps",
        "q": f"restaurants near {location} with no wait time",
        "type": "search",
        "api_key": Config.SERPAPI_API_KEY
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        results = res.get("local_results", [])
        if not results:
            return f"No alternative restaurants found in {location}."
        
        # Sort by rating
        sorted_places = sorted(results, key=lambda x: x.get("rating", 0), reverse=True)[:3]
        
        clean_data = []
        for p in sorted_places:
            clean_data.append({
                "title": p.get("title"),
                "rating": p.get("rating"),
                "address": p.get("address"),
                "note": "Selected for low wait time"
            })
        return json.dumps(clean_data)
    except Exception as e:
        return f"Alt Restaurant Search Error: {str(e)}"

@tool
def indoor_places_tool(location: str):
    """
    Finds indoor attractions like museums, galleries, and malls.
    Use this when weather is poor (rain, snow, extreme heat).
    """
    params = {
        "engine": "google_maps",
        "q": f"indoor activities museums malls in {location}",
        "type": "search",
        "api_key": Config.SERPAPI_API_KEY
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        results = res.get("local_results", [])
        if not results:
            return f"No indoor places found in {location}."
            
        sorted_places = sorted(results, key=lambda x: x.get("rating", 0), reverse=True)[:4]
        
        clean_data = []
        for p in sorted_places:
            clean_data.append({
                "title": p.get("title"),
                "type": p.get("type"),
                "rating": p.get("rating"),
                "address": p.get("address")
            })
        return json.dumps(clean_data)
    except Exception as e:
        return f"Indoor Place Search Error: {str(e)}"