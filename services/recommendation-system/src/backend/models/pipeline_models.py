from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class PipelineState(TypedDict, total=False):
    """
    State object for the vector-only recommendation pipeline
    Compatible with LangGraph's state handling
    """
    # Input
    user_id: str
    top_k: int
    
    # Pipeline data
    user_embedding: Optional[List[float]]
    high_rating_videos: Optional[List[Dict[str, Any]]]
    candidate_videos: Optional[List[Dict[str, Any]]]
    final_list: Optional[List[Dict[str, Any]]]
    
    # Test feature data
    rejected_videos: Optional[List[Dict[str, Any]]]  # Videos below threshold
    all_candidate_videos: Optional[List[Dict[str, Any]]]  # Before filtering
    capture_rejected: Optional[bool]  # Flag to enable rejected video capture
    
    # Pipeline metadata
    pipeline_step: str
    error: Optional[str]
    is_new_user: bool
    execution_time: Optional[float]
    newsletter_id: Optional[int]
