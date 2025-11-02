FROM python:3.12-slim

WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy the app
COPY . .

# listen on 0.0.0.0
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

# start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]