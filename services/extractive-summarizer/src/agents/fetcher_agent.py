from typing import Dict, Any
from youtube.fetcher import fetch_videos_for_subdomain
from db.mongo_client import insert_metadata
from qdrant.qdrant_client import insert_title_desc
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
        insert_metadata(
            video_id=video["video_id"],
            published_date=video["published_date"],
            title=video["title"],
            views=video["views"],
            description=video["description"],
            subdomain=subdomain
        )
        # Generate embedding for title+description
        vector = embed_title_desc(video["title"], video["description"])

        # Insert embedding in Qdrant
        insert_title_desc(
            video_id=video["video_id"],
            vector=vector.tolist() if hasattr(vector, "tolist") else vector,
            metadata={
                "video_id": video["video_id"],
                "published_date": video["published_date"]
            }
        )
        videos.append(video)

    # Return updated state
    return {**state, "videos": videos}
