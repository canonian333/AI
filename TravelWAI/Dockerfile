FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the ports used by the application:
# 8501 for Streamlit (Frontend)
# 8000 for FastAPI (Backend)
EXPOSE 8501 8000

# Healthcheck for Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command to start the Streamlit frontend.
# If you want to run the FastAPI server, you can override the command when running the container:
# docker run -p 8000:8000 <image_name> uvicorn server:app --host 0.0.0.0 --port 8000
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
