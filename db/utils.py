"""
Database utility functions for schema extraction and inspection.
"""

import logging
from typing import Dict, List, Any

from db.connection import get_db_inspector
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def get_database_schema() -> str:
    """
    Retrieve complete database schema with table names, columns, types, and samples.
    Returns formatted string suitable for LLM context.
    """
    try:
        inspector = get_db_inspector()
        tables = inspector.get_table_names()
        
        if not tables:
            return "No tables found in the database."
        
        schema_text = "DATABASE SCHEMA:\n" + "=" * 80 + "\n\n"
        
        for table_name in tables:
            schema_text += f"TABLE: `{table_name}`\n"
            schema_text += "-" * 80 + "\n"
            
            # Get columns
            columns = inspector.get_columns(table_name)
            schema_text += "COLUMNS:\n"
            for col in columns:
                schema_text += f"  - `{col['name']}` ({col['type']})\n"
            
            schema_text += "\n"
        
        schema_text += "=" * 80 + "\n"
        return schema_text
    
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving database schema: {e}")
        return f"Error retrieving schema: {str(e)}"


def get_table_sample(table_name: str, limit: int = 2) -> Dict[str, Any]:
    """
    Get sample rows from a specific table for context.
    Returns dict with columns and sample data.
    """
    try:
        from db.connection import get_db_connection
        from sqlalchemy import text
        
        connection = get_db_connection()
        query = text(f"SELECT * FROM `{table_name}` LIMIT :limit")
        result = connection.execute(query, {"limit": limit})
        
        rows = result.fetchall()
        columns = result.keys()
        
        connection.close()
        
        return {
            "table_name": table_name,
            "columns": list(columns),
            "sample_rows": [dict(row) for row in rows]
        }
    
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving sample from {table_name}: {e}")
        return {
            "table_name": table_name,
            "error": str(e)
        }
