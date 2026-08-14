"""
WSGI wrapper for Chainlit application on Vercel.
Chainlit uses Starlette/FastAPI internally, which is ASGI.
This wrapper converts ASGI to WSGI for Vercel compatibility.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app as chainlit_app

# Chainlit creates a Starlette app internally
# Export it for Vercel
app = chainlit_app
