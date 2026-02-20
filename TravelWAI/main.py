import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 1. Load Environment Variables First
load_dotenv() 

# 2. Force initialization for LangSmith (Tracing)
os.environ["LANGCHAIN_TRACING_V2"] = "true" 
os.environ["LANGCHAIN_PROJECT"] = "TravelWAI_MSc"

# 3. Imports (now that env is set)
from app.config import Config
from app.agent import agent_executor
from app.database import MongoStore
from app.evaluator import PlanEvaluator

# 4. Initialize and Validate
Config.validate()
db = MongoStore()
evaluator = PlanEvaluator()

st.set_page_config(page_title="TravelWAI", page_icon="🌍", layout="wide")

st.title("🌍 TravelWAI: Your AI Travel Planner")
st.markdown("### Plan your perfect trip with AI")

# --- UI INPUT SECTION ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("From (Origin)", value="Bangalore", placeholder="City, Airport")
        destination = st.text_input("To (Destination)", value="Paris", placeholder="City, Country")
    
    with col2:
        # Default to next weekend
        today = datetime.now()
        next_friday = today + timedelta((4 - today.weekday()) % 7)
        dates = st.date_input(
            "Travel Dates", 
            value=(next_friday, next_friday + timedelta(days=3)),
            min_value=today
        )

    col3, col4, col5 = st.columns(3)
    with col3:
        travelers = st.number_input("Travelers", min_value=1, max_value=10, value=2)
    with col4:
        budget = st.slider("Budget per person (₹)", min_value=5000, max_value=500000, value=50000, step=5000)
    with col5:
        food_pref = st.selectbox("Food Preference", ["No Preference", "Vegetarian", "Non-Vegetarian", "Vegan", "Halal"])

    interests = st.multiselect(
        "Interests / Activities",
        ["Sightseeing", "Relaxation", "Adventure", "History", "Shopping", "Nightlife", "Food & Drink"],
        default=["Sightseeing", "Food & Drink"]
    )

    plan_button = st.button("Generate Detailed Itinerary ✈️", use_container_width=True, type="primary")

# --- LOGIC ---
if plan_button:
    # 1. Construct the natural language prompt for the agent
    if len(dates) == 2:
        date_str = f"from {dates[0]} to {dates[1]}"
    else:
        date_str = f"starting {dates[0]}"
        
    user_prompt = (
        f"Plan a trip from {origin} to {destination} {date_str} for {travelers} people. "
        f"Budget is approximately ₹{budget} per person. "
        f"Food preference: {food_pref}. "
        f"Interests: {', '.join(interests)}."
    )
    
    # Display the constructed request
    with st.expander("Review your request", expanded=False):
        st.write(user_prompt)

    # 2. Existing Agent Execution Logic
    with st.spinner("Agent is researching flights, hotels, and attractions... (This may take a minute)"):
        try:
            # We pass a list of messages as the 'messages' key
            result = agent_executor.invoke(
                {"messages": [("user", user_prompt)]},
                config={"run_name": "Travel Agent Workflow"}
            )
            
            # The agent returns the whole state
            # Prefer 'final_itinerary' if available (new workflow), else fallback to last message
            plan = result.get("final_itinerary", result["messages"][-1].content)
            
        except Exception as e:
            # Fallback for when the chain fails
            st.error(f"An error occurred during planning: {str(e)}")
            st.warning("Trying to salvage partial plan...")
            plan = "⚠️ Plan generation was interrupted. Please try again in a few minutes or simplify your request."

    # 3. Display Result
    st.markdown("---")
    st.subheader("Your AI Travel Itinerary")
    st.markdown(plan)
    
    # 4. Evaluation & Saving
    if "⚠️" not in plan:
        with st.status("Evaluating and Saving Plan..."):
            eval_json = evaluator.grade_plan(user_prompt, plan)
            st.write(f"Critic Score: {eval_json}")
            
            save_data = {
                "user_prompt": user_prompt,
                "itinerary": plan,
                "evaluation": str(eval_json)
            }
            
            if db.save_plan(save_data):
                st.write("Plan securely saved. ✅")
            else:
                st.error("Failed to save plan. Is the FastAPI server running?")

# Sidebar Info
with st.sidebar:
    st.header("About")
    st.info("TravelWAI uses advanced AI agents to plan your perfect trip.")
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("- Groq (Llama-3)")
    st.markdown("- LangGraph")
    st.markdown("- SerpAPI")