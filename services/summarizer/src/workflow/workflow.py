from langgraph.graph import StateGraph, END
from typing import Dict
from agents.summarizer_agent import summarization_agent
from agents.mongo_update_agent import mongo_update_agent


workflow = StateGraph(dict)
workflow.add_node("summarization_agent", summarization_agent)
workflow.add_node("mongo_update_agent", mongo_update_agent)
workflow.set_entry_point("summarization_agent")
workflow.add_edge("summarization_agent", "mongo_update_agent")
workflow.add_edge("mongo_update_agent", END)

summary_graph = workflow.compile()