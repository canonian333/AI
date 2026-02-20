from typing import Annotated, List, TypedDict, Dict, Any
import json
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_groq import ChatGroq
from app.config import Config
from app.tools import search_places

# --- State Definition ---
class TravelState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    parsed_trip: Dict[str, Any]
    sightseeing_plan: Dict[str, Any]
    dining_plan: Dict[str, Any]
    final_itinerary: str

# --- LLM Setup ---
# 1. Small, Cost-Efficient Model (Llama-3-8b)
llm_small = ChatGroq(
    model_name=Config.SMALL_MODEL_NAME, 
    groq_api_key=Config.GROQ_API_KEY, 
    temperature=0,
    max_retries=3,
    request_timeout=60
)

# 2. Large, Capable Model (Llama-3-70b)
llm_large = ChatGroq(
    model_name=Config.MODEL_NAME, 
    groq_api_key=Config.GROQ_API_KEY, 
    temperature=0,
    max_retries=3,
    request_timeout=60
)


# --- Chains (Internal Logic) ---

def parse_safely(response):
    """Helper to parse JSON from LLM response"""
    text = response.content.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "")
    try:
        return json.loads(text)
    except:
        return {"error": "Failed to parse JSON", "raw": text}

# --- Nodes ---

def trip_parser_node(state: TravelState):
    """
    Step 1: Parse Raw Input -> Structured Data
    Model: Small LLM
    """
    last_message = state["messages"][-1]
    user_input = last_message.content
    
    system_msg = SystemMessage(content=(
        "You are a strict data extractor. Extract the following trip details from the user request:\n"
        "- origin (city/airport)\n"
        "- destination (city/country)\n"
        "- dates (start_date, end_date or duration)\n"
        "- budget (total or per person with currency)\n"
        "- travelers (count)\n"
        "- interests (list of preferences)\n"
        "\n"
        "Return STRICT JSON only. No markdown, no conversational text."
    ))
    
    response = llm_small.invoke([system_msg, HumanMessage(content=user_input)])
    parsed_trip = parse_safely(response)
    
    # Validation fallback if empty
    if "destination" not in parsed_trip:
        parsed_trip["destination"] = "Unknown"
        
    return {"parsed_trip": parsed_trip}


def generators_node(state: TravelState):
    """
    Step 2: Parallel Generation
    - Sightseeing Skeleton (Small LLM)
    - Dining Plan (Tool + Small LLM)
    Uses RunnableParallel to execute both streams concurrently.
    """
    parsed_trip = state["parsed_trip"]
    destination = parsed_trip.get("destination", "Paris")
    interests = parsed_trip.get("interests", [])
    
    # --- Stream A: Sightseeing ---
    def generate_sightseeing(inputs):
        prompt = (
            f"Create a structured day-wise sightseeing skeleton for a trip to {destination}.\n"
            f"Interests: {interests}\n"
            f"Duration: {inputs.get('dates', '3 days')}\n"
            "Rules:\n"
            "1. List 2-3 main attractions per day.\n"
            "2. Group by proximity.\n"
            "3. Return STRICT JSON: {'Day 1': ['Place A', 'Place B'], ...}\n"
            "No descriptions."
        )
        resp = llm_small.invoke([SystemMessage(content=prompt)])
        return parse_safely(resp)

    # --- Stream B: Dining ---
    def generate_dining(inputs):
        # 1. Tool Call (External API)
        # Search for restaurants based on budget/preference
        pref = "restaurants"
        if "vegetarian" in str(interests).lower():
            pref = "vegetarian restaurants"
            
        try:
            # Invoking the tool directly to get raw data
            # search_places is a structured tool, we use .invoke
            raw_data = search_places.invoke({"location": destination, "preference": pref})
        except Exception as e:
            raw_data = f"Error fetching data: {str(e)}"
            
        # 2. Filter & Organize (Small LLM)
        prompt = (
            f"You are a dining logic engine. Review these candidate restaurants in {destination}:\n"
            f"{raw_data}\n\n"
            "Select the best 2-3 unique options for lunch/dinner.\n"
            "Return STRICT JSON: {'lunch': 'Name', 'dinner': 'Name'}\n"
            "No explanations."
        )
        resp = llm_small.invoke([SystemMessage(content=prompt)])
        return parse_safely(resp)

    # Run in parallel
    chain = RunnableParallel({
        "sightseeing": RunnableLambda(generate_sightseeing),
        "dining": RunnableLambda(generate_dining)
    })
    
    results = chain.invoke(parsed_trip)
    
    return {
        "sightseeing_plan": results["sightseeing"],
        "dining_plan": results["dining"]
    }


def synthesis_node(state: TravelState):
    """
    Step 3: Final Composition
    Model: Large LLM
    Synthesizes structured data into a polished itinerary.
    """
    parsed_trip = state["parsed_trip"]
    sightseeing = state["sightseeing_plan"]
    dining = state["dining_plan"]
    
    system_msg = SystemMessage(content=(
        "You are a Senior Travel Agent. Compose a final, polished itinerary based on the provided structured data.\n"
        "Do NOT re-plan. Use the provided skeletons.\n"
        "\n"
        "DATA SOURCES:\n"
        f"1. Trip Details: {json.dumps(parsed_trip)}\n"
        f"2. Sightseeing Skeleton: {json.dumps(sightseeing)}\n"
        f"3. Dining Recommendations: {json.dumps(dining)}\n"
        "\n"
        "INSTRUCTIONS:\n"
        "- Generate a sleek, day-by-day narrative.\n"
        "- Add logical flow (morning -> afternoon -> evening).\n"
        "- Include specific sections for 'Transport to Destination' and 'Accommodation Code' (suggest 2-3 hotels).\n"
        "- Format nicely with Markdown (bolding, lists).\n"
        "- Keep it professional and engaging, but not overly verbose.\n"
        "- Add a budget summary at the end."
    ))
    
    response = llm_large.invoke([system_msg])
    
    return {
        "final_itinerary": response.content,
        "messages": [response] # Append final response to history
    }


# --- Graph Construction ---
workflow = StateGraph(TravelState)

# Nodes
workflow.add_node("trip_parser", trip_parser_node)
workflow.add_node("generators", generators_node)
workflow.add_node("synthesizer", synthesis_node)

# Edges (Linear Pipeline)
workflow.add_edge(START, "trip_parser")
workflow.add_edge("trip_parser", "generators")
workflow.add_edge("generators", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile
app_graph = workflow.compile()