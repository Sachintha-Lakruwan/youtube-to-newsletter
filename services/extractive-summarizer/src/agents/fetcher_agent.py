from typing import Dict, Any
from youtube.fetcher import fetch_videos_for_subdomain
from db.mongo_client import insert_metadata
from qdrant.qdrant_cli import insert_title_desc
from embeddings.embedder import embed_title_desc

def fetch_youtube_videos_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph agent node to fetch YouTube videos for a subdomain.
    
    Input state:
        state["subdomain"] -> keyword/topic to search
    Output state:
        state["videos"] -> list of video metadata dicts
    """
    subdomain = state.get("subdomain")
    if not subdomain:
        raise ValueError("State must contain 'subdomain' key.")

    # fetch videos using fetcher.py function
    video_items = fetch_videos_for_subdomain(subdomain)

    # inserting metadata to MongoDB and building video list for langraph workflow state
    videos = []
    for video in video_items:
        videos.append(video)

    # Return updated state
    return {**state, "videos": videos}
