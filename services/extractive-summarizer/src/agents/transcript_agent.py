from typing import Dict, Any
from youtube.transcript import fetch_transcript
from db.mongo_client import summaries_collection
from db.supabase_client import insert_video
from qdrant.qdrant_cli import insert_title_desc
from embeddings.embedder import embed_title_desc
def transcript_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph agent node to fetch transcripts for all videos in state["videos"].
    Stores transcript in MongoDB (summaries collection).
    Stores metadata in SupaBase and metadata embeddings in Qdrant
    """
    videos = state.get("videos", [])
    if not videos:
        raise ValueError("No videos found in state['videos'].")

    processed_videos = []

    for video in videos:
        video_id = video["video_id"]
        transcript_text = fetch_transcript(video_id)

        if transcript_text == "No transcript available":
            # Skip videos without transcripts
            continue

        video["transcript"] = transcript_text
        processed_videos.append(video)

        # Store metadata in Supabase
        insert_video(video)

        # Generate embedding and store in Qdrant
        vector = embed_title_desc(video["title"], video["description"])
        insert_title_desc(
            video_id=video_id,
            vector=vector.tolist() if hasattr(vector, "tolist") else vector,
            metadata={
                "video_id": video_id,
                "published_date": video["published_date"]
            }
        )

        # Store transcript in MongoDB
        summaries_collection.update_one(
            {"video_id": video_id},
            {"$set": {"transcript": transcript_text}},
            upsert=True
        )

    return {**state, "videos": processed_videos}
