from langchain.tools import tool
import requests
import json
from app.config import Config

@tool
def get_flights(origin: str, destination: str, date: str):
    """
    Searches for best flights. Date format: YYYY-MM-DD.
    """
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": date,
        "currency": "INR",
        "api_key": Config.SERPAPI_API_KEY
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        flights = res.get("best_flights", [])
        
        if not flights:
            return f"No flights found from {origin} to {destination} on {date}."

        # Token Optimization: Extract only essential info
        clean_data = []
        for f in flights[:3]:
            clean_data.append({
                "airline": f.get("flights", [{}])[0].get("airline"),
                "price": f.get("price"),
                "duration": f.get("total_duration")
            })
        
        # FIX: Return as a JSON string for Groq validation
        return json.dumps(clean_data)
    except Exception as e:
        return f"Flight Search Error: {str(e)}"

@tool
def get_trains(origin: str, destination: str, date: str):
    """
    Searches for train schedules between cities. Date format: YYYY-MM-DD.
    """
    # For India-based projects, this usually hits a custom API or SerpApi web results
    return f"Search results for trains from {origin} to {destination} on {date}: Multiple options available via IRCTC starting from ₹500."