FROM python:3.12-slim

WORKDIR /app

# 1. copy requirements FIRST
COPY requirements.txt /app/requirements.txt

# 2. install deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# 3. copy the rest of the app
COPY . /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]