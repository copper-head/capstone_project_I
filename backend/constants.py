from pathlib import Path
from dotenv import dotenv_values

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

ENV = dotenv_values(ENV_PATH)

# Container listens on 0.0.0.0; match compose exposed port
API_ADDRESS = "0.0.0.0"
API_PORT = 8000

# Use service name for in-network DB host
DB_CONFIG = {
    "DB_HOST": "postgres",
    "DB_PORT": 5432,
    "DB_NAME": "mydatabase",
    "DB_USER": ENV.get("DB_USER", "test"),
    "DB_PASSWORD": ENV.get("DB_PASSWORD", "test"),
}