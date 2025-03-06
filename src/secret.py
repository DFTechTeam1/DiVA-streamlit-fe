import os
from dotenv import load_dotenv


env_file = os.getenv("ENV_FILE", "env/.env.development")

if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file)
else:
    raise FileNotFoundError(f"Environment file not found: {env_file}")


class Config:
    NAS_PORT_1 = os.getenv("NAS_PORT_1")
    NAS_PORT_2 = os.getenv("NAS_PORT_2")
    NAS_USERNAME = os.getenv("NAS_USERNAME")
    NAS_PASSWORD = os.getenv("NAS_PASSWORD")
    NAS_IP_1 = os.getenv("NAS_IP_1")
    NAS_IP_2 = os.getenv("NAS_IP_2")
    NAS_IP_3 = os.getenv("NAS_IP_3")
    NAS_IP_4 = os.getenv("NAS_IP_4")
    NAS_IP_5 = os.getenv("NAS_IP_5")
    BASE_API = os.getenv("BASE_API")
    IMAGE_QUERY = os.getenv("IMAGE_QUERY")
    IMAGE_QUERY_API = f"{BASE_API}{IMAGE_QUERY}"
