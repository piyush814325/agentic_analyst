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
echo ""
echo "===================================================================="
echo "[SUCCESS] All checks passed!"
echo ""
echo "Starting Chainlit application..."
echo "The UI will open at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "===================================================================="
echo ""

# Start Chainlit
chainlit run app.py -w
