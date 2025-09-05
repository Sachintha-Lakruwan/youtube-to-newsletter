from typing import Dict, Any
import logging
from backend.services.retrieval_service import retrieval_service
from backend.models.pipeline_models import PipelineState

logger = logging.getLogger(__name__)

def vector_retrieval_node(state: PipelineState) -> PipelineState:
    """
    Vector similarity search with filtering and time decay
    """
    try:
        if not state.get("user_id"):
            logger.error("No user_id provided for retrieval")
            state["candidate_videos"] = []
            state["rejected_videos"] = []
            state["pipeline_step"] = "retrieval_completed"
            return state
        
        # Check if this is a test mode (when we need rejected videos)
        capture_rejected = state.get("capture_rejected", False)
        print(capture_rejected)
        
        if capture_rejected:
            # Get both accepted and rejected videos for test purposes
            retrieval_result = retrieval_service.retrieve_videos_for_user(
                user_id=state["user_id"],
                similarity_threshold=0.4,  # Lower threshold to get more candidates
                limit=100,
                time_decay_days=30,
                decay_factor=0.1,
                capture_rejected=True
            )

            candidate_videos = retrieval_result["accepted"]
            rejected_videos = retrieval_result["rejected"]
            
            state["candidate_videos"] = candidate_videos
            state["rejected_videos"] = rejected_videos
            state["all_candidate_videos"] = candidate_videos + rejected_videos
            
            logger.info(f"Vector retrieval completed: {len(candidate_videos)} candidates, {len(rejected_videos)} rejected")
        else:
            # Normal retrieval without capturing rejected videos
            candidate_videos = retrieval_service.retrieve_videos_for_user(
                user_id=state["user_id"],
                similarity_threshold=0.6,
                limit=100,
                time_decay_days=30,
                decay_factor=0.1,
                capture_rejected=False
            )
            
            state["candidate_videos"] = candidate_videos
            state["rejected_videos"] = []
            
            logger.info(f"Vector retrieval completed: {len(candidate_videos)} candidates")
        
        state["pipeline_step"] = "vector_retrieval_completed"
        
        # Debug: Ensure the state is properly set
        logger.info(f"DEBUG: After setting, state['candidate_videos'] length: {len(state['candidate_videos']) if state.get('candidate_videos') else 0}")
        logger.info(f"DEBUG: State type: {type(state)}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in vector_retrieval_node: {str(e)}")
        state["error"] = str(e)
        state["pipeline_step"] = "error"
        return state
