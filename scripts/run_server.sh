#!/bin/sh

show_help() {
  echo "Usage: sh scripts/run_server.sh [ --development | --staging | --production | --help ]"
  echo ""
  echo "--development    Run the server on localhost and load the .env.development file"
  echo "--staging        Run the server on the staging IP and load the .env.staging file"
  echo "--production     Run the server on the production IP address and load the .env.production file"
  echo "--help           Show this help message"
}

if [ -z "$1" ]; then
  echo "Error: No environment specified. Please provide one of --development, --staging, or --production."
  show_help
  exit 1
fi

ENV_FILE=""
DEFAULT_PORT="15000"

case "$1" in
  --development)
    echo "Using development environment configuration"
    export ENV_FILE="env/.env.development"
    ;;
  --staging)
    echo "Using staging environment configuration"
    export ENV_FILE="env/.env.staging"
    ;;
  --production)
    echo "Using production environment configuration"
    export ENV_FILE="env/.env.production"
    ;;
  --help)
    show_help
    exit 0
    ;;
  *)
    echo "Invalid option: $1"
    show_help
    exit 1
    ;;
esac

export $(grep -v '^#' $ENV_FILE | xargs)

if [ -z "$APPLICATION_PORT" ]; then
  echo "Warning: APPLICATION_PORT not provided in $ENV_FILE. Using default port $DEFAULT_PORT."
  APPLICATION_PORT=$DEFAULT_PORT
fi


echo "Checking OS Environment"
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
  echo "WSL detected"
  . .venv/bin/activate
else
  case "$OSTYPE" in
    linux*)
      echo "Linux based OS detected"
      source .venv/bin/activate
      ;;
    darwin*)
      echo "macOS detected"
      source .venv/bin/activate
      ;;
    cygwin* | msys* | mingw*)
      echo "Windows based OS detected"
      source .venv/Scripts/activate
      ;;
    *)
      echo "Unsupported OS."
      exit 1
      ;;
  esac
fi

echo "Starting server on port $APPLICATION_PORT..."
streamlit run src/main.py --server.port $APPLICATION_PORT
