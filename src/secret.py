import os
from dotenv import load_dotenv


env_file = os.getenv('ENV_FILE', 'env/.env.development')

if os.path.exists(env_file):
	load_dotenv(dotenv_path=env_file)
else:
	raise FileNotFoundError(f'Environment file not found: {env_file}')


QUERY_API = os.getenv('QUERY_API')
APPLICATION_PORT = os.getenv('APPLICATION_PORT')
