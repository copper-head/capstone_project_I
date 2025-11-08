FROM python:3.12-slim

WORKDIR /app

# 1. copy requirements FIRST (so layer caching works)
COPY requirements.txt /app/requirements.txt

# 2. install python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# 3. copy the rest of the app
COPY . /app

EXPOSE 8000 5432

# Default command: start the FastAPI app with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]