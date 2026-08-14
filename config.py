"""
Global configuration for database and LLM setup.
Loads environment variables and initializes connection strings.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment variables")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    logger.warning("SUPABASE_URL not found in environment variables")
if not SUPABASE_ANON_KEY:
    logger.warning("SUPABASE_ANON_KEY not found in environment variables")

# PostgreSQL Database Configuration (Supabase)
# Prefer DATABASE_URL when explicitly provided; otherwise allow server-side projects to use
# a direct Postgres connection string as a fallback.
DB_CONNECTION_STRING = (
    os.getenv("DATABASE_URL")
    or os.getenv("SUPABASE_DB_URL")
    or "postgresql+psycopg2://postgres:password@localhost:5432/postgres"
)

# Ensure connection string uses psycopg2 driver
if DB_CONNECTION_STRING and "postgresql://" in DB_CONNECTION_STRING:
    # Replace postgresql:// with postgresql+psycopg2:// for SQLAlchemy
    DB_CONNECTION_STRING = DB_CONNECTION_STRING.replace(
        "postgresql://", "postgresql+psycopg2://"
    )

# Application Configuration
APP_DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"

logger.info("Database: PostgreSQL (Supabase)")
logger.info(f"Supabase URL configured: {'Yes' if SUPABASE_URL else 'No'}")
logger.info(f"Supabase anon key configured: {'Yes' if SUPABASE_ANON_KEY else 'No'}")
logger.info(f"Groq API Key configured: {'Yes' if GROQ_API_KEY else 'No'}")
