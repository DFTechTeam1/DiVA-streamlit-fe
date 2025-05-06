#!/bin/bash

show_help() {
  echo "Usage: bash scripts/run_server.sh [ --development | --staging | --production ] [ --port ]"
  echo ""
  echo "--development    Run the server on localhost and load the .env.development file"
  echo "--staging        Run the server on the staging IP and load the .env.staging file"
  echo "--production     Run the server on the production IP address and load the .env.production file"
  echo "--help           Show this help message"
  echo ""
  echo "Example: "
  echo "sh scripts/run_server.sh --development --22000"
}

# Validate first argument (environment)
if [ -z "$1" ]; then
  echo "Error: No environment specified. Please provide one of --development, --staging, or --production."
  show_help
  exit 1
fi

ENV_FILE=""
APPLICATION_PORT="15000"

# Handle environment selection
case "$1" in
  --development)
    echo "Using development environment configuration"
    ENV_FILE="env/.env.development"
    ;;
  --staging)
    echo "Using staging environment configuration"
    ENV_FILE="env/.env.staging"
    ;;
  --production)
    echo "Using production environment configuration"
    ENV_FILE="env/.env.production"
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

# Handle custom port (optional)
if [ -n "$2" ]; then
  if echo "$2" | grep -qE "^--[0-9]+$"; then
    APPLICATION_PORT=$(echo "$2" | sed 's/^--//')
  else
    echo "Invalid port format. Use --<port> (e.g., --22000)"
    exit 1
  fi
fi

# Load environment variables from .env file safely
if [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
else
  echo "Environment file '$ENV_FILE' not found."
  exit 1
fi

# Detect and activate virtual environment
echo "Checking OS Environment"
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
  echo "WSL detected"
  . .venv/bin/activate
else
  case "$OSTYPE" in
    linux*)   echo "Linux OS detected" && source .venv/bin/activate ;;
    darwin*)  echo "macOS detected" && source .venv/bin/activate ;;
    cygwin* | msys* | mingw*) echo "Windows OS detected" && source .venv/Scripts/activate ;;
    *) echo "Unsupported OS." && exit 1 ;;
  esac
fi

echo "Starting server on port $APPLICATION_PORT"
streamlit run src/main.py --server.port $APPLICATION_PORT
