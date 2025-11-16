import os
from dotenv import load_dotenv
from pathlib import Path

# In general if this is a container keep the address to '0.0.0.0' to allow access from outside the container.
# If you want to test locally set it to '127.0.0.1' or 'localhost'
API_ADDRESS = '0.0.0.0'

# MAKE SURE THAT IF YOU CHANGE THIS PORT THAT THE PORT IS FORWARDED IN DOCKER
# Check docker-compose.yml to see this.
API_PORT = 9000

# Locate .env one level above the backend directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DB_CONFIG = {
    'DB_HOST': 'postgres',
    'DB_PORT': 5432,
    'DB_NAME': 'mydatabase',
    'DB_USER': os.getenv('DB_USERNAME'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD')
}

AI_API_KEY = os.getenv('AI_API_KEY')