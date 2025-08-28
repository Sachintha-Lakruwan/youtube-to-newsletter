from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from workflow.workflow import summary_graph

app = FastAPI(title="YouTube Summarizer Microservice")

class VideoRequest(BaseModel):
    video_ids: List[str]

@app.post("/summarize")
def generate_summaries(request: VideoRequest):
    state = {"video_ids": request.video_ids}
    
    # Run the two-agent workflow
    final_state = summary_graph.invoke(state)
    
    # Return processed videos with abstractive summaries
    return {
        "status": "success",
        "processed_videos": final_state.get("videos", [])
    }