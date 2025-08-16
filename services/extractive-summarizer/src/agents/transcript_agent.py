from typing import Dict, Any
from youtube.transcript import fetch_transcript
from db.mongo_client import summaries_collection

def transcript_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph agent node to fetch transcripts for all videos in state["videos"].
    Stores transcript in MongoDB (summaries collection).
    """
    videos = state.get("videos", [])
    if not videos:
        raise ValueError("No videos found in state['videos'].")

    for video in videos:
        video_id = video["video_id"]
        transcript_text = fetch_transcript(video_id)
        video["transcript"] = transcript_text  # Add to workflow state

        # Store transcript in MongoDB 
        summaries_collection.update_one(
            {"video_id": video_id},
            {"$set": {"transcript": transcript_text}},
            upsert=True
        )

    return {**state, "videos": videos}
