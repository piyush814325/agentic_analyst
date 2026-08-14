"""
LangGraph state machine workflow definition.
Orchestrates the flow between nodes and handles conditional routing.
"""

import logging
from langgraph.graph import StateGraph, END
from typing import Literal, Any

from agent.state import AgentState
from agent.nodes import (
    schema_inspector,
    sql_generator,
    sql_executor,
    self_corrector,
    result_summarizer
)

logger = logging.getLogger(__name__)


def should_self_correct(state: AgentState) -> Literal["self_correct", "summarize"]:
    """
    Conditional routing after SQL execution.
    If error exists and retries < 3, go to self-correct.
    Otherwise go to summarize.
    """
    error_exists = state.get("error_message") is not None
    retry_count = state.get("retry_count", 0)
    
    if error_exists and retry_count < 3:
        logger.info(f"Routing to self_correct (retry {retry_count + 1})")
        return "self_correct"
    else:
        logger.info("Routing to summarize")
        return "summarize"


def build_agent_graph() -> Any:
    """
    Build the complete LangGraph workflow.
    
    Flow:
    schema_inspector -> sql_generator -> sql_executor
                                            |
                                    [has error & retries < 3?]
                                          /        \
                                       YES          NO
                                      /              \
                              self_corrector    result_summarizer -> END
                                    |
                              sql_executor
    """
    
    # Create state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("schema_inspector", schema_inspector)
    workflow.add_node("sql_generator", sql_generator)
    workflow.add_node("sql_executor", sql_executor)
    workflow.add_node("self_corrector", self_corrector)
    workflow.add_node("summarizer", result_summarizer)
    
    # Add edges
    workflow.add_edge("schema_inspector", "sql_generator")
    workflow.add_edge("sql_generator", "sql_executor")
    
    # Conditional edge from sql_executor
    workflow.add_conditional_edges(
        "sql_executor",
        should_self_correct,
        {
            "self_correct": "self_corrector",
            "summarize": "summarizer"
        }
    )
    
    # After self-correction, try execution again
    workflow.add_edge("self_corrector", "sql_executor")
    
    # Final edge to end
    workflow.add_edge("summarizer", END)
    
    # Set entry point
    workflow.set_entry_point("schema_inspector")
    
    logger.info("LangGraph workflow built successfully")
    
    return workflow.compile()


# Global agent graph instance
agent_graph = None


def get_agent_graph():
    """Get or create the compiled agent graph."""
    global agent_graph
    if agent_graph is None:
        agent_graph = build_agent_graph()
    return agent_graph
