#!/bin/bash

# RUNTIME startup script for FastAPI backend
# Handles both production and development modes with debugpy support
# Environment variables:
#   - DEBUGPY_ENABLED: if set to "true", enables debugpy
#   - DEBUGPY_WAIT: if set to "true", waits for a debugger to connect
#   - DEBUGPY_PORT: port for debugpy to listen on
#   - APP_RUNTIME: runtime environment (tilt, kubernetes, etc.)
#   - APP_ENV: application environment (development, production, etc.)
#   - HOST: host to listen on
#   - PORT: port to listen on
# NOTE: variables referenced here are suppplied by Tilt config/secrets (ultimately manifest files)

set -e

# Default values
DEBUGPY_ENABLED=${DEBUGPY_ENABLED:-"false"}
DEBUGPY_WAIT=${DEBUGPY_WAIT:-"false"}
DEBUGPY_PORT=${DEBUGPY_PORT:-"5678"}
APP_RUNTIME=${APP_RUNTIME:-"unknown"}
APP_ENV=${APP_ENV:-"production"}
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-"8000"}

# Activate virtual environment if it exists (for local development)
if [ -f ".venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

echo "🚀 Starting FastAPI backend..."
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   App Runtime: $APP_RUNTIME"
echo "   App Environment: $APP_ENV"
echo "   Debugpy Enabled: $DEBUGPY_ENABLED"
echo "   Debugpy Wait: $DEBUGPY_WAIT"
echo "   Install Dev Dependencies: $INSTALL_DEV_DEPS"

# Check if we should use debugpy
if [ "$APP_ENV" = "development" ]; then
    echo "🔧 Starting in development mode with live reload"
    if [ "$DEBUGPY_ENABLED" = "true" ]; then
        if [ "$INSTALL_DEV_DEPS" != "true" ]; then
            echo "❌ ERROR: DEBUGPY_ENABLED is set to true and it requires development dependencies to be installed."
            echo "💬 Update your .env file and set the INSTALL_DEV_DEPS environment variable to true"
        fi
        echo "🪲 debugpy support on port $DEBUGPY_PORT"
        DEBUGPY_ARGS="--listen 0.0.0.0:$DEBUGPY_PORT"
        if [ "$DEBUGPY_WAIT" = "true" ]; then
            DEBUGPY_ARGS="$DEBUGPY_ARGS --wait"
        fi
        
        echo "🪲 Debugpy args: $DEBUGPY_ARGS"
        echo "🪲 Full command: python -Xfrozen_modules=off -m debugpy $DEBUGPY_ARGS -m uvicorn src.main:app --host $HOST --port $PORT --reload"
        
        # Start with debugpy
        exec python -Xfrozen_modules=off -m debugpy $DEBUGPY_ARGS -m uvicorn src.main:app --host $HOST --port $PORT --reload
    else
        if [ "$INSTALL_DEV_DEPS" = "true" ]; then
            echo "⚠️ Debugpy available but not used. Starting without debugpy."
        fi
        
        exec python -m uvicorn src.main:app --host $HOST --port $PORT --reload
    fi
else
    echo "🏭 Starting in production mode"
    exec python -m uvicorn src.main:app --host $HOST --port $PORT
fi 