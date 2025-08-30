from typing import Dict, Any
from youtube.summary import generate_extractive_summary, store_extractive_summary

def summarizer_agent(state: Dict[str, Any], top_k=8, alpha=0.7) -> Dict[str, Any]:
    """
    LangGraph agent to generate extractive summaries for all videos in state['videos'].
    Uses separate functions for generation and storage (MongoDB + Qdrant).
    This is the final step, so no need to update workflow state with summary.
    """
    videos = state.get("videos", [])
    if not videos:
        raise ValueError("No videos found in state['videos'].")

    for video in videos:
        video_id = video["video_id"]
        transcript = video.get("transcript", "")
        if not transcript:
            print(f"[Summarizer] No transcript for video {video_id}, skipping...")
            continue

        # Generate extractive summary and store it in mongodb and it's embedding in qdrant
        extractive_summary = generate_extractive_summary(transcript, top_k=top_k, alpha=alpha)
        
        store_extractive_summary(video_id=video_id, extractive_summary=extractive_summary)

    return state  # return state unchanged
