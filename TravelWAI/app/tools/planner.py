from langchain_core.messages import AIMessage

def planner_agent(state: dict):
    # Check if raw_data exists, simpler safety check
    raw_data = state.get("raw_data", {})
    raw_sights = raw_data.get("sights", [])
    
    # Simple Clustering Logic: Group by neighborhood in address string
    clusters = {}
    for place in raw_sights:
        # Safety check for address structure
        address_parts = place.get("address", "General").split(",")
        if len(address_parts) >= 2:
            neighborhood = address_parts[-2].strip()
        else:
            neighborhood = "General"
            
        if neighborhood not in clusters:
            clusters[neighborhood] = []
        clusters[neighborhood].append(place.get("title"))
        
    return {"clusters": clusters, "messages": [AIMessage(content="Locations clustered by neighborhood.")]}