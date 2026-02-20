import requests
import os

class MongoStore:
    def __init__(self):
        # Pointing to your new FastAPI bridge
        self.url = "http://localhost:8000/v1/save-plan"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": os.getenv("INTERNAL_API_KEY")
        }

    def save_plan(self, plan_json):
        try:
            response = requests.post(self.url, json=plan_json, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"REST API Error: {e}")
            return False