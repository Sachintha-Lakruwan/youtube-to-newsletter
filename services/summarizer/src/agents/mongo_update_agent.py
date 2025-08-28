from db.mongo_client import summaries_collection
from typing import Dict

def update_abstractive_summary(video_id: str, abstractive_summary: str):
    summaries_collection.update_one(
        {"video_id": video_id},
        {"$set": {"abstractive_summary": abstractive_summary}}
    )

def mongo_update_agent(state: Dict) -> Dict:
    for video in state.get("videos", []):
        update_abstractive_summary(video["video_id"], video["abstractive_summary"])
    return state