# app/evaluator.py
from langchain_groq import ChatGroq
from app.config import Config

class PlanEvaluator:
    def __init__(self):
        # Linked to the same model as the agent
        self.critic = ChatGroq(
            model_name=Config.MODEL_NAME, 
            groq_api_key=Config.GROQ_API_KEY,
            temperature=0,
            max_retries=3,
            request_timeout=60
        )

    def grade_plan(self, user_prompt, plan):
        prompt = (
            f"You are a travel critic. Review this plan against the request.\n"
            f"Request: {user_prompt}\nPlan: {plan}\n"
            "Provide a score (1-10) and a brief critique."
        )
        try:
            return self.critic.invoke(prompt).content
        except Exception as e:
            return f"Critic currently unavailable: {str(e)}"