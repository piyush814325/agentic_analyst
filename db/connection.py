"""
Database connection lifecycle management using SQLAlchemy.
Handles engine initialization, connection pooling, and safe shutdown.
"""

import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from config import DB_CONNECTION_STRING, APP_DEBUG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLAlchemy engine and connection lifecycle."""
    
    _engine = None
    
    @classmethod
    def get_engine(cls):
        """Get or create the SQLAlchemy engine with connection pooling."""
        if not DB_CONNECTION_STRING:
            logger.warning(
                "Database is not configured. Add DATABASE_URL from Supabase Settings -> Database -> Connection string -> URI."
            )
            return None

        if cls._engine is None:
            try:
                connect_args = {}
                if "supabase.co" in DB_CONNECTION_STRING or "postgresql://" in DB_CONNECTION_STRING:
                    connect_args = {"sslmode": "require"}

                cls._engine = create_engine(
                    DB_CONNECTION_STRING,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_recycle=3600,
                    echo=APP_DEBUG,
                    connect_args=connect_args,
                )
                with cls._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("Database engine initialized and connection tested successfully")
            except SQLAlchemyError as e:
                logger.error(f"Failed to initialize database engine: {e}")
                raise
        return cls._engine
    
    @classmethod
    def close(cls):
        """Close the engine and dispose of all connections."""
        if cls._engine is not None:
            try:
                cls._engine.dispose()
                logger.info("Database engine disposed successfully")
                cls._engine = None
            except SQLAlchemyError as e:
                logger.error(f"Error closing database engine: {e}")
    
    @classmethod
    def get_connection(cls):
        """Get a new database connection from the pool."""
        try:
            engine = cls.get_engine()
            return engine.connect()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    @classmethod
    def get_inspector(cls):
        """Get a SQLAlchemy inspector for schema introspection."""
        try:
            engine = cls.get_engine()
            return inspect(engine)
        except SQLAlchemyError as e:
            logger.error(f"Failed to create inspector: {e}")
            raise


def get_db_engine():
    """Convenience function to get database engine."""
    return DatabaseManager.get_engine()


def get_db_connection():
    """Convenience function to get database connection."""
    return DatabaseManager.get_connection()


def get_db_inspector():
    """Convenience function to get database inspector."""
    return DatabaseManager.get_inspector()
