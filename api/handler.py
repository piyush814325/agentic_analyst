"""
Vercel API Handler for Chainlit Application
This creates a serverless function endpoint for Vercel deployment.
Chainlit will run as a backend service in this handler.
"""

from http.server import BaseHTTPRequestHandler
import os
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Set up environment
os.environ.setdefault('PYTHONUNBUFFERED', '1')

class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler for the Chainlit app.
    """
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/health':
            self.wfile.write(b'{"status": "ok"}')
        elif self.path == '/':
            self.wfile.write(b'{"message": "Agentic SQL Data Analyst - API Handler"}')
        else:
            self.wfile.write(b'{"error": "Not found"}')
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"message": "POST received"}')
