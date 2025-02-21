import os
from dotenv import load_dotenv


env_file = os.getenv("ENV_FILE", "env/.env.development")

if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file)
else:
    raise FileNotFoundError(f"Environment file not found: {env_file}")


class Config:
    BASE_API = os.getenv("BASE_API")
    IMAGE_QUERY = os.getenv("IMAGE_QUERY")
    IMAGE_QUERY_API = f"{BASE_API}{IMAGE_QUERY}"
