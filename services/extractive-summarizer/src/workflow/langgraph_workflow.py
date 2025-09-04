from langgraph.graph import StateGraph, END
from agents.fetcher_agent import fetch_youtube_videos_agent
from agents.transcript_agent import transcript_agent
from agents.summary_agent import summarizer_agent
from agents.newsletter_summary_agent import editor_agent
from typing import TypedDict, List, Dict, Any

class Video(TypedDict):
    video_id: str
    title: str
    transcript: str
    

class GraphState(TypedDict):
    subdomain: str
    videos: List[Video]

def build_youtube_graph():
    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("fetch_videos", fetch_youtube_videos_agent)
    builder.add_node("fetch_transcripts", transcript_agent)
    builder.add_node("summarize_videos", summarizer_agent)
    builder.add_node("create_newsletter_summary",editor_agent)

    # Entry point
    builder.set_entry_point("fetch_videos")

    # Connect edges
    builder.add_edge("fetch_videos", "fetch_transcripts")
    builder.add_edge("fetch_transcripts", "summarize_videos")
    builder.add_edge("summarize_videos", "create_newsletter_summary")
    builder.add_edge("create_newsletter_summary",END)

    # Compile graph
    graph = builder.compile()
    return graph
