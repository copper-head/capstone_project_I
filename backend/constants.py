from pathlib import Path
from dotenv import dotenv_values

# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
print(ENV_PATH)

ENV = dotenv_values(ENV_PATH)
print("DATA COOL: " + str(ENV))


# In general if this is a container keep the address to '0.0.0.0' to allow access from outside the container.
# If you want to test locally set it to '127.0.0.1' or 'localhost'
API_ADDRESS = '0.0.0.0'

# MAKE SURE THAT IF YOU CHANGE THIS PORT THAT THE PORT IS FORWARDED IN DOCKER
# Check docker-compose.yml to see this.
API_PORT = 9000


DB_CONFIG = {
    'DB_HOST': 'postgres',
    'DB_PORT': 5432,
    'DB_NAME': 'mydatabase',
    'DB_USER': ENV['DB_USER'],
    'DB_PASSWORD': ENV['DB_PASSWORD'],
}