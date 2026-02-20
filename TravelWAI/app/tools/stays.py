from langchain.tools import tool
import requests
import json
from app.config import Config

@tool
def get_hotels(location: str, check_in: str, check_out: str):
    """
    Finds top-rated hotels. Dates: YYYY-MM-DD.
    """
    params = {
        "engine": "google_hotels",
        "q": location,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "currency": "INR",
        "api_key": Config.SERPAPI_API_KEY
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        hotels = res.get("properties", [])

        if not hotels:
            return f"No hotels found in {location} for the selected dates."

        # Sort by high rating and extract essential info
        top_hotels = sorted(hotels, key=lambda x: x.get("rating", 0), reverse=True)[:6]
        
        clean_data = []
        for h in top_hotels:
            clean_data.append({
                "name": h.get("name"),
                "price": h.get("rate_per_night", {}).get("lowest"),
                "rating": h.get("rating"),
                "amenities": h.get("amenities", [])[:3]
            })

        return json.dumps(clean_data) #
    except Exception as e:
        return f"Hotel Search Error: {str(e)}"