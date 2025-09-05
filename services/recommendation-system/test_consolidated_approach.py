#!/usr/bin/env python3
"""
Test script to verify the consolidated recommendation approach works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from backend.pipelines.orchestrator import recommendation_orchestrator

def test_consolidated_approach():
    """Test both normal and test modes using the same function"""
    
    test_user_id = "test_user_123"
    
    print("=== Testing Normal Mode ===")
    try:
        normal_result = recommendation_orchestrator.generate_recommendations(
            user_id=test_user_id,
            top_k=4,
            test_mode=False
        )
        
        print(f"Normal mode result keys: {list(normal_result.keys())}")
        print(f"Recommendations count: {len(normal_result.get('recommendations', []))}")
        print(f"Has newsletter_id: {'newsletter_id' in normal_result}")
        
    except Exception as e:
        print(f"Normal mode error: {str(e)}")
    
    print("\n=== Testing Test Mode ===")
    try:
        test_result = recommendation_orchestrator.generate_recommendations(
            user_id=test_user_id,
            top_k=4,
            test_mode=True,
            num_rejected=4
        )
        
        print(f"Test mode result keys: {list(test_result.keys())}")
        print(f"Recommended videos count: {len(test_result.get('recommended_videos', []))}")
        print(f"Rejected videos count: {len(test_result.get('rejected_videos', []))}")
        print(f"Has newsletter_id: {'newsletter_id' in test_result}")
        
    except Exception as e:
        print(f"Test mode error: {str(e)}")
    
    print("\n=== Testing Legacy Test Function ===")
    try:
        legacy_result = recommendation_orchestrator.generate_test_recommendations(
            user_id=test_user_id,
            num_recommended=4,
            num_rejected=4
        )
        
        print(f"Legacy test result keys: {list(legacy_result.keys())}")
        print(f"Recommended videos count: {len(legacy_result.get('recommended_videos', []))}")
        print(f"Rejected videos count: {len(legacy_result.get('rejected_videos', []))}")
        
    except Exception as e:
        print(f"Legacy test mode error: {str(e)}")

if __name__ == "__main__":
    test_consolidated_approach()
