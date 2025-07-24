from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from career_agent.career_states import CareerState
from career_agent.career_analyzer import validate_user_inputs, analyze_career_predictions, rank_career_recommendations
# from career_approval import request_user_approval, finalize_recommendation, get_approval_decision

# SQLite checkpointer for career graph
career_db = sqlite3.connect("career_graph.db", check_same_thread=False)
career_memorybox = SqliteSaver(career_db)

def create_career_graph():
    """Create a simpler career graph without approval workflow."""
    graph = StateGraph(CareerState)
    
    # Add nodes
    graph.add_node("validate_inputs", validate_user_inputs)
    graph.add_node("analyze_predictions", analyze_career_predictions)
    graph.add_node("rank_recommendations", rank_career_recommendations)
    
    # Set entry point
    graph.set_entry_point("validate_inputs")
    
    # Add edges
    graph.add_edge("validate_inputs", "analyze_predictions")
    graph.add_edge("analyze_predictions", "rank_recommendations")
    
    # Set finish point
    graph.set_finish_point("rank_recommendations")
    
    return graph.compile() 