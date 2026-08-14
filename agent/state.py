"""
LangGraph state definitions using TypedDict.
Defines the data structure flowing through the agent graph.
"""

from typing import TypedDict, Optional, List, Any, Union
from typing_extensions import Annotated
import operator


class AgentState(TypedDict):
    """
    Complete state for the SQL agent workflow.
    Flows through LangGraph nodes for schema inspection, SQL generation, execution, and correction.
    """
    # Input
    user_query: str
    
    # Schema information
    table_schema: str
    
    # SQL generation and execution
    generated_sql: str
    
    # Query results
    query_result: Union[List[dict], None]
    
    # Rows affected by write/DDL operations
    rows_affected: Optional[int]
    
    # Error tracking
    error_message: Optional[str]
    
    # Retry logic
    retry_count: int
    
    # Final output
    final_answer: str
    
    # Execution trace for debugging
    execution_trace: Annotated[List[str], operator.add]
