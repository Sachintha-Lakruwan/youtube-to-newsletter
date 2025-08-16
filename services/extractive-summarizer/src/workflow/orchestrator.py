from typing import List, Dict, Any
from workflow.langgraph_workflow import build_youtube_graph

def orchestrator_agent(subdomains: List[str]) -> Dict[str, Any]:
    """
    Orchestrator agent to run the YouTube-to-newsletter workflow
    for multiple subdomains.
    
    Returns a dictionary with final workflow state per subdomain.
    """
    final_states = {}

    # Build the workflow graph once
    graph = build_youtube_graph()

    for subdomain in subdomains:
        print(f"[Orchestrator] Starting workflow for subdomain: {subdomain}")
        initial_state: Dict[str, Any] = {"subdomain": subdomain, "videos": []}

        try:
            # Run LangGraph workflow for this subdomain
            state_after_run = graph.run(initial_state=initial_state)
            final_states[subdomain] = state_after_run
            print(f"[Orchestrator] Completed workflow for subdomain: {subdomain}")
        except Exception as e:
            print(f"[Orchestrator] Error processing subdomain {subdomain}: {e}")
            final_states[subdomain] = {"error": str(e)}

    return final_states
