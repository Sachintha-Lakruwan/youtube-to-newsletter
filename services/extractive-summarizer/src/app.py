from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from workflow.orchestrator import orchestrator_agent

# FastAPI app
app = FastAPI(title="YouTube to Newsletter Workflow", version="1.0")

# Pydantic request model
class WorkflowRequest(BaseModel):
    subdomains: List[str]

# Pydantic response model (optional, dynamic)
class WorkflowResponse(BaseModel):
    results: Dict[str, Any]

@app.post("/run-workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):
    """
    Trigger the YouTube-to-newsletter workflow for given subdomains.
    """
    subdomains = request.subdomains
    if not subdomains:
        raise HTTPException(status_code=400, detail="No subdomains provided.")

    try:
        # Call orchestrator to run the workflow for all subdomains
        results = orchestrator_agent(subdomains=subdomains)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "ok"}
