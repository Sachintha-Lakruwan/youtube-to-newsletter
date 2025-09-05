from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Service for handling video retrieval operations using only vector similarity search
    with user embeddings, filtering watched videos, and applying time decay
    """
    
    def __init__(self):
        # No embedding model needed since we use user embeddings directly
        logger.info("RetrievalService initialized for vector-only retrieval")
    
    def retrieve_videos_for_user(self, user_id: str, 
                                similarity_threshold: float = 0.6, 
                                limit: int = 100,
                                time_decay_days: int = 30,
                                decay_factor: float = 0.02,
                                capture_rejected: bool = False) -> List[Dict[str, Any]]:
        """
        Main retrieval function: 
        1. Get user embedding from Supabase
        2. Perform vector similarity search in Qdrant
        3. Filter out previously watched videos
        4. Apply time decay penalty based on publish date
        
        Args:
            capture_rejected: If True, returns dict with accepted/rejected videos
        """
        try:
            from backend.database.supabase_client import supabase_client
            from backend.database.qdrant_client import qdrant_client
            import random
            
            # Step 1: Get user embedding
            user_embedding = supabase_client.get_user_embedding(user_id)
            if not user_embedding:
                logger.warning(f"No user embedding found for {user_id}")
                if capture_rejected:
                    return {"accepted": [], "rejected": []}
                return []
            
            logger.info(f"Retrieved user embedding for {user_id}: {len(user_embedding)} dimensions")
            
            if capture_rejected:
                # Use very low threshold to get a large pool of videos
                all_videos = qdrant_client.vector_similarity_search(
                    query_embedding=user_embedding,
                    similarity_threshold=0.1,  # Very low threshold to capture more videos
                    limit=limit * 3  # Get even more videos
                )
                
                logger.info(f"Vector search returned {len(all_videos) if all_videos else 0} videos with threshold 0.1")
                
                if not all_videos:
                    logger.warning(f"No videos found for user {user_id} even with very low threshold")
                    return {"accepted": [], "rejected": []}
                
                # Use a more reasonable threshold for separation to ensure we get rejected videos
                adjusted_threshold = 0.4  # Lower than original 0.6 to get more rejected videos
                
                # Separate videos based on adjusted similarity threshold
                candidate_videos = []
                rejected_videos = []
                
                for video in all_videos:
                    # Check both 'score' and 'similarity' fields
                    score = video.get("score", video.get("similarity", 0))
                    video["score"] = score  # Normalize to 'score' field
                    
                    if score >= adjusted_threshold:
                        candidate_videos.append(video)
                    else:
                        rejected_videos.append(video)
                
                logger.info(f"Separated videos: {len(candidate_videos)} candidates (score >= {adjusted_threshold}), {len(rejected_videos)} rejected (score < {adjusted_threshold})")
                
                # Debug: Log some sample scores
                if all_videos:
                    sample_scores = [v.get("score", v.get("similarity", 0)) for v in all_videos[:5]]
                    logger.info(f"Sample scores from first 5 videos: {sample_scores}")
                
                # If we still don't have rejected videos, force create some from the lower scoring candidates
                if len(rejected_videos) == 0 and len(all_videos) > 10:
                    # Sort all videos by score and take the bottom 30% as rejected
                    all_videos_sorted = sorted(all_videos, key=lambda x: x.get("score", x.get("similarity", 0)), reverse=True)
                    split_point = int(len(all_videos_sorted) * 0.7)  # Top 70% as candidates, bottom 30% as rejected
                    candidate_videos = all_videos_sorted[:split_point]
                    rejected_videos = all_videos_sorted[split_point:]
                    logger.info(f"Forced separation: {len(candidate_videos)} candidates, {len(rejected_videos)} rejected (bottom 30%)")
                
            else:
                # Normal mode - use standard threshold
                candidate_videos = qdrant_client.vector_similarity_search(
                    query_embedding=user_embedding,
                    similarity_threshold=similarity_threshold,
                    limit=limit
                )
                
                logger.info(f"Vector search returned {len(candidate_videos) if candidate_videos else 0} videos with threshold {similarity_threshold}")
                
                if not candidate_videos:
                    logger.warning(f"No similar videos found for user {user_id}")
                    return []
                
                rejected_videos = []
            
            # Step 3: Get user's previously watched videos
            watched_video_ids = set(supabase_client.get_user_watched_videos(user_id))
            logger.info(f"Filtering out {len(watched_video_ids)} previously watched videos")
            
            # Filter out watched videos
            unmatched_videos = [
                video for video in candidate_videos 
                if video.get("video_id") not in watched_video_ids
            ]
            
            if capture_rejected:
                # Also filter watched videos from rejected set
                rejected_unmatched = [
                    video for video in rejected_videos 
                    if video.get("video_id") not in watched_video_ids
                ]
                logger.info(f"After filtering rejected videos: {len(rejected_unmatched)} unwatched rejected videos from {len(rejected_videos)} total rejected")
            else:
                rejected_unmatched = []
            
            logger.info(f"After filtering: {len(unmatched_videos)} unwatched videos from {len(candidate_videos)} candidates")
            
            # Step 4: Apply time decay penalty
            videos_with_time_decay = self._apply_time_decay_penalty(
                unmatched_videos, 
                time_decay_days, 
                decay_factor
            )
            
            # Sort by final score (similarity + time decay)
            videos_with_time_decay.sort(key=lambda x: x.get("final_score", 0), reverse=True)
            
            if capture_rejected:
                # Return both accepted and rejected videos
                import random
                random.shuffle(rejected_unmatched)
                
                logger.info(f"Vector search: {len(videos_with_time_decay)} candidates for pipeline, {len(rejected_unmatched)} rejected from similarity threshold")
                
                return {
                    "accepted": videos_with_time_decay,
                    "rejected": rejected_unmatched
                }
            else:
                # Return only accepted videos (normal mode)
                logger.info(f"Retrieved {len(videos_with_time_decay)} videos for user {user_id}")
                return videos_with_time_decay
            
        except Exception as e:
            logger.error(f"Error in retrieve_videos_for_user for {user_id}: {str(e)}")
            if capture_rejected:
                return {"accepted": [], "rejected": []}
            return []
    
    def _apply_time_decay_penalty(self, videos: List[Dict[str, Any]], 
                                 time_decay_days: int = 30, 
                                 decay_factor: float = 0.02) -> List[Dict[str, Any]]:
        """
        Apply time decay penalty based on video publish date from videos table
        Recent videos get boosted, older videos get penalized
        """
        try:
            from backend.database.supabase_client import supabase_client
            
            if not videos:
                return []
            
            # Get video IDs for publish date lookup
            video_ids = [video.get("video_id") for video in videos if video.get("video_id")]
            
            # Get publish dates from videos table
            publish_dates = supabase_client.get_video_publish_dates(video_ids)
            
            current_time = datetime.utcnow()
            processed_videos = []
            
            for video in videos:
                video_copy = video.copy()
                video_id = video.get("video_id")
                
                # Get original similarity score
                similarity_score = video.get("similarity", 0.0)
                
                # Get publish date
                publish_date_str = publish_dates.get(video_id)
                time_penalty = 0.0
                
                if publish_date_str:
                    try:
                        # Parse publish date
                        publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
                        days_old = (current_time - publish_date).days
                        
                        if days_old > time_decay_days:
                            # Apply penalty for old videos
                            excess_days = days_old - time_decay_days
                            time_penalty = decay_factor * (excess_days / time_decay_days)
                            # Cap penalty at 60% of similarity score
                            time_penalty = min(time_penalty, similarity_score * 0.6)
                        else:
                            # Slight boost for recent videos
                            recency_boost = decay_factor * (time_decay_days - days_old) / time_decay_days
                            time_penalty = -recency_boost  # Negative penalty = boost
                        
                        video_copy["days_old"] = days_old
                        video_copy["publish_date"] = publish_date_str
                        
                    except Exception as e:
                        logger.warning(f"Error parsing publish date for video {video_id}: {str(e)}")
                        time_penalty = 0.0
                else:
                    # No publish date available, apply moderate penalty
                    time_penalty = decay_factor * 0.7
                    video_copy["days_old"] = None
                
                # Calculate final score
                final_score = similarity_score - time_penalty
                video_copy["time_penalty"] = time_penalty
                video_copy["final_score"] = max(final_score, 0.0)  # Ensure non-negative
                
                processed_videos.append(video_copy)
            
            logger.info(f"Applied time decay to {len(processed_videos)} videos")
            return processed_videos
            
        except Exception as e:
            logger.error(f"Error applying time decay penalty: {str(e)}")
            # Return original videos with similarity as final score
            for video in videos:
                video["final_score"] = video.get("similarity", 0.0)
                video["time_penalty"] = 0.0
            return videos
# check this function and it needed or not
    def apply_mmr_diversity(self, videos: List[Dict[str, Any]], 
                           query_embedding: Optional[List[float]] = None,
                           lambda_param: float = 0.7, 
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Apply Maximal Marginal Relevance (MMR) for diversity filtering
        Balances relevance to query with diversity among selected items
        """
        try:
            logger.info(f"MMR diversity starting with {len(videos)} videos, top_k={top_k}")
            
            if not videos or len(videos) <= top_k:
                logger.info(f"Returning all {len(videos)} videos (less than or equal to top_k)")
                return videos[:top_k]
            
            if not query_embedding:
                # If no query embedding, just return top scored videos
                logger.warning("No query embedding provided, using simple scoring")
                return sorted(videos, key=lambda x: x.get("final_score", 0), reverse=True)[:top_k]
            
            logger.info(f"Query embedding dimension: {len(query_embedding)}")
            
            # Convert embeddings to numpy arrays for efficient computation
            query_emb = np.array(query_embedding)
            
            # Get embeddings for all videos
            video_embeddings = []
            valid_videos = []
            
            for i, video in enumerate(videos):
                embedding = video.get("embedding")
                if embedding and len(embedding) == 768:
                    video_embeddings.append(np.array(embedding))
                    valid_videos.append(video)
                else:
                    # If no embedding, use zero vector (low diversity impact)
                    logger.warning(f"Video {i} missing or invalid embedding, using zero vector")
                    video_embeddings.append(np.zeros(768))
                    valid_videos.append(video)
            
            logger.info(f"Processing {len(valid_videos)} valid videos for MMR")
            
            if not video_embeddings:
                logger.warning("No video embeddings available")
                return videos[:top_k]
            
            video_embeddings = np.array(video_embeddings)
            
            # MMR algorithm
            selected_indices = []
            remaining_indices = list(range(len(valid_videos)))
            
            for iteration in range(min(top_k, len(valid_videos))):
                if not remaining_indices:
                    break
                
                best_score = -float('inf')
                best_idx = None
                
                for idx in remaining_indices:
                    # Relevance score (use final_score which includes time decay)
                    relevance = valid_videos[idx].get("final_score", 0.0)
                    
                    # Diversity score (maximum similarity to already selected items)
                    max_similarity = 0.0
                    if selected_indices:
                        similarities = [
                            self._cosine_similarity(video_embeddings[idx], video_embeddings[sel_idx])
                            for sel_idx in selected_indices
                        ]
                        max_similarity = max(similarities)
                    
                    # MMR score
                    mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                    
                    if mmr_score > best_score:
                        best_score = mmr_score
                        best_idx = idx
                
                if best_idx is not None:
                    selected_indices.append(best_idx)
                    remaining_indices.remove(best_idx)
                    logger.debug(f"MMR iteration {iteration+1}: selected video with score {best_score:.4f}")
            
            # Return selected videos with MMR scores
            selected_videos = []
            for i, idx in enumerate(selected_indices):
                video = valid_videos[idx].copy()
                video["mmr_rank"] = i + 1
                video["mmr_score"] = best_score  # This would be calculated per video in a full implementation
                selected_videos.append(video)
            
            logger.info(f"MMR diversity completed: selected {len(selected_videos)} videos")
            return selected_videos
            
        except Exception as e:
            logger.error(f"Error applying MMR diversity: {str(e)}")
            # Fallback to simple scoring
            return sorted(videos, key=lambda x: x.get("final_score", 0), reverse=True)[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        """
        try:
            # Handle zero vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(np.dot(vec1, vec2) / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
# Global service instance
retrieval_service = RetrievalService()
