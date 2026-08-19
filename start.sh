#!/bin/bash
# Startup script for Agentic SQL Data Analyst on Linux/macOS

echo ""
echo "===================================================================="
echo "  Agentic SQL Data Analyst - Startup Script"
echo "===================================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "[INFO] Checking dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found"
    echo "[INFO] Creating .env from .env.example..."
    cp .env.example .env
    echo "[INFO] Please edit .env with your actual credentials"
    echo ""
    read -p "Press Enter to continue..."
fi

# Display startup info
PORT="${CHAINLIT_PORT:-8000}"
for p in $(seq 8000 8100); do
    if python3 - "$p" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
try:
    s.bind(("127.0.0.1", port))
except OSError:
    raise SystemExit(1)
finally:
    s.close()
PY
    then
        PORT="$p"
        break
    fi
done

if [ "$PORT" = "" ]; then
    echo "[ERROR] No free port found between 8000 and 8100."
    exit 1
fi

echo ""
echo "===================================================================="
echo "[SUCCESS] All checks passed!"
echo ""
echo "Starting Chainlit application..."
echo "The UI will open at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo "===================================================================="
echo ""

# Start Chainlit
chainlit run app.py -w --port "$PORT"
