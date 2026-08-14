"""
Dynamic data ingestion from CSV/Excel files.
Infers schema, sanitizes names, and creates/populates MySQL tables.
"""

import logging
import re
import pandas as pd
from pathlib import Path
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.types import TypeDecorator, VARCHAR
from typing import Tuple, Dict, List, Any

from db.connection import get_db_engine

logger = logging.getLogger(__name__)


class DataTypeMapper:
    """Maps Pandas/Python types to SQLAlchemy column types."""
    
    @staticmethod
    def infer_sql_type(series: pd.Series) -> Any:
        """Infer optimal SQLAlchemy type from pandas Series."""
        dtype = series.dtype
        
        # Check for datetime
        if dtype == 'datetime64[ns]':
            return DateTime()
        
        # Check for boolean
        if dtype == 'bool':
            return Boolean()
        
        # Check for integer
        if dtype in ['int64', 'int32', 'int16', 'int8']:
            return Integer()
        
        # Check for float
        if dtype in ['float64', 'float32']:
            return Float()
        
        # Check for string/object
        if dtype == 'object':
            # Try to infer max length
            max_len = series.astype(str).str.len().max()
            max_len = min(int(max_len * 1.2 + 10), 1000)  # Add 20% buffer, cap at 1000
            if max_len > 500:
                return Text()
            return VARCHAR(max_len)
        
        # Default to VARCHAR
        return VARCHAR(255)


class TableNameSanitizer:
    """Sanitizes table and column names for MySQL compatibility."""
    
    # MySQL reserved keywords (partial list of common ones)
    MYSQL_KEYWORDS = {
        'select', 'from', 'where', 'insert', 'update', 'delete', 'create',
        'alter', 'drop', 'table', 'database', 'column', 'key', 'index',
        'primary', 'foreign', 'join', 'order', 'group', 'by', 'limit',
        'offset', 'union', 'all', 'and', 'or', 'not', 'in', 'like', 'between',
        'is', 'null', 'on', 'inner', 'left', 'right', 'full', 'outer', 'cross',
        'set', 'values', 'check', 'default', 'unique', 'constraint'
    }
    
    @staticmethod
    def sanitize_name(name: str, is_table: bool = False) -> str:
        """
        Sanitize table or column name for MySQL.
        - Convert to lowercase
        - Replace spaces and special chars with underscores
        - Remove leading numbers
        - Prefix with underscore if starts with number
        - Keep only alphanumeric and underscores
        """
        # Convert to string and lowercase
        name = str(name).strip().lower()
        
        # Replace spaces and special characters with underscores
        name = re.sub(r'[^a-z0-9_]', '_', name)
        
        # Remove leading underscores/numbers, or prefix if starts with digit
        name = re.sub(r'^([0-9])', r'_\1', name)
        
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove trailing underscores
        name = name.rstrip('_')
        
        # Ensure minimum length
        if not name:
            name = 'col' if not is_table else 'table'
        
        # For table names, ensure uniqueness and MySQL keyword avoidance
        if is_table and name in TableNameSanitizer.MYSQL_KEYWORDS:
            name = f"tbl_{name}"
        elif not is_table and name in TableNameSanitizer.MYSQL_KEYWORDS:
            name = f"col_{name}"
        
        return name


class DataIngestionEngine:
    """Handles CSV/Excel file parsing and MySQL table creation."""
    
    @staticmethod
    def read_file(file_path: str) -> pd.DataFrame:
        """Read CSV or Excel file into DataFrame."""
        file_path = Path(file_path)
        
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            logger.info(f"Successfully read file {file_path.name}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    @staticmethod
    def create_table_from_dataframe(
        df: pd.DataFrame,
        table_name: str = None,
        if_exists: str = "replace"
    ) -> Tuple[str, List[str], int, Dict[str, str]]:
        """
        Create or populate MySQL table from DataFrame.
        
        Args:
            df: Pandas DataFrame to ingest
            table_name: Optional custom table name (auto-generated if None)
            if_exists: 'fail', 'replace', or 'append'
        
        Returns:
            Tuple of (table_name, columns, row_count, schema_dict)
        """
        try:
            # Generate table name if not provided
            if table_name is None:
                table_name = "imported_data"
            
            # Sanitize table name
            table_name = TableNameSanitizer.sanitize_name(table_name, is_table=True)
            
            # Sanitize column names
            df_sanitized = df.copy()
            df_sanitized.columns = [
                TableNameSanitizer.sanitize_name(col, is_table=False)
                for col in df.columns
            ]
            
            # Build schema dictionary for reference
            schema_dict = {}
            for col in df_sanitized.columns:
                col_type = DataTypeMapper.infer_sql_type(df_sanitized[col])
                schema_dict[col] = str(col_type)
            
            # Write to MySQL using SQLAlchemy
            engine = get_db_engine()
            df_sanitized.to_sql(
                table_name,
                con=engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            row_count = len(df_sanitized)
            columns = list(df_sanitized.columns)
            
            logger.info(
                f"Table '{table_name}' created/populated: "
                f"{row_count} rows, {len(columns)} columns"
            )
            
            return table_name, columns, row_count, schema_dict
        
        except Exception as e:
            logger.error(f"Error creating table from DataFrame: {e}")
            raise
    
    @staticmethod
    def ingest_file(
        file_path: str,
        table_name: str = None,
        if_exists: str = "replace"
    ) -> Dict[str, Any]:
        """
        Complete ingestion pipeline: read file and create table.
        
        Returns:
            Dictionary with ingestion results and metadata
        """
        try:
            # Read file
            df = DataIngestionEngine.read_file(file_path)
            
            # Create table
            table_name, columns, row_count, schema_dict = DataIngestionEngine.create_table_from_dataframe(
                df, table_name, if_exists
            )
            
            # Sample first 2 rows for preview
            sample_data = df.head(2).to_dict('records')
            
            result = {
                "success": True,
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count,
                "schema": schema_dict,
                "sample_data": sample_data,
                "file_path": str(file_path)
            }
            
            logger.info(f"Ingestion successful: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path)
            }
