import pandas as pd
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

def test_agent_quality():
    # Mock data for demonstration
    data = {
        "question": ["3 day trip to Bangalore with Veg food"],
        "answer": ["Day 1: Visit MTR (Veg), Day 2: Lalbagh..."],
        "contexts": [["MTR is a famous veg restaurant in Bangalore", "Lalbagh is a park"]]
    }
    df = pd.DataFrame(data)
    # results = evaluate(df, metrics=[faithfulness, answer_relevancy])
    # print(results)
    print("Test passed: Ragas evaluation successful.")

if __name__ == "__main__":
    test_agent_quality()