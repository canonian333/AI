# TravelWAI Tests (`tests/`)

This directory is intended for unit and integration testing of the TravelWAI application.

## Test Files

*   **`test_agent.py`**: A script designed to evaluate the AI agent's response quality. 
    *   It is set up to utilize the `ragas` evaluation framework to assess metrics like **faithfulness** (ensuring the answer is derived from the context) and **answer_relevancy** (ensuring the answer addresses the user's prompt).
    *   Currently, it defines a basic structure using `pandas` and mock data to demonstrate how the evaluation pipeline would operate.
