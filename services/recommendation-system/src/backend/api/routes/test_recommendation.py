from fastapi import APIRouter, Query
from typing import List, Dict, Any
from backend.pipelines.orchestrator import recommendation_orchestrator

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def test_recommendations(
    user_id: str = Query(..., description="User ID"),
    num_recommended: int = Query(4, description="Number of recommended videos to return"),
    num_rejected: int = Query(4, description="Number of rejected videos to return")
):
    """
    Test endpoint that returns top recommended videos and random rejected videos
    from the vector retrieval stage for analysis purposes.
    
    Returns:
    - recommended_videos: Top N videos after full pipeline processing
    - rejected_videos: Random N videos that were rejected during vector retrieval
    - metadata: Execution details and statistics
    """
    result = recommendation_orchestrator.generate_recommendations(
        user_id=user_id,
        top_k=num_recommended,
        test_mode=True,
        num_rejected=num_rejected
    )
    return result