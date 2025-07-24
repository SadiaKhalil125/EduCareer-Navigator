from langgraph.graph import StateGraph
from advisor_agent.universitiesstates import systemState
from advisor_agent.UnisRecomender import find_universities
from advisor_agent.UnisRanker import rank_unis
from advisor_agent.approval import approve_decision, final_decision
from advisor_agent.recommendfinalized import returnfinalized
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


# SQLite checkpointer
db = sqlite3.connect("graph.db", check_same_thread=False)
memorybox = SqliteSaver(db)

def create_advisor_graph():
    graph = StateGraph(systemState)


    graph.add_node("find_universities", find_universities)
    graph.add_node("rank_unis", rank_unis)
    graph.add_node("approve_decision", approve_decision)
    graph.add_node("recommend_finalized_universities", returnfinalized)

    graph.set_entry_point("find_universities")

    graph.add_edge("find_universities", "approve_decision")
    graph.add_conditional_edges("approve_decision", final_decision)
    graph.add_edge("rank_unis", "recommend_finalized_universities")

    graph.set_finish_point("recommend_finalized_universities")
    return graph.compile()
