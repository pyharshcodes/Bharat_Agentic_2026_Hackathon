"""
Jan-Sahayak AI - Production FastAPI Server
Serves the Interactive Web Dashboard, REST Endpoints, and PDF Dossier Downloads.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.orchestrator import JanSahayakOrchestrator
from agent.profile_parser import DEMO_PERSONAS

app = FastAPI(
    title="Jan-Sahayak AI (जन-सहायक) API",
    description="Autonomous Civic & Welfare Delivery Agent for Bharat — BharatAgentic Hackathon 2026",
    version="1.0.0"
)

# Enable CORS for universal compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize master orchestrator
orchestrator = JanSahayakOrchestrator()

# Directory references
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


class AgentRunRequest(BaseModel):
    persona_id: Optional[str] = None
    custom_query: Optional[str] = None
    language: Optional[str] = "Hindi"
    draft_grievance: Optional[bool] = False
    profile_overrides: Optional[Dict[str, Any]] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Jan-Sahayak AI",
        "version": "1.0.0",
        "sandbox_ready": True
    }


@app.get("/api/personas")
def get_personas():
    """Returns the list of demo personas available for 1-click testing."""
    summary = []
    for pid, p in DEMO_PERSONAS.items():
        summary.append({
            "id": pid,
            "name": p["name"],
            "role": f"{p['occupation']} ({p['state']})",
            "income": f"₹{p['annual_income']:,.0f}/yr",
            "highlight": p.get("specific_need", ""),
            "has_grievance": bool(p.get("grievance_case"))
        })
    return {"personas": summary}


@app.post("/api/run")
def run_agent(req: AgentRunRequest):
    """
    Main agent execution endpoint. Runs the full multi-agent cognitive pipeline.
    """
    try:
        # Determine payload
        payload = {}
        if req.persona_id and req.persona_id in DEMO_PERSONAS:
            payload = dict(DEMO_PERSONAS[req.persona_id])
            if req.profile_overrides:
                payload.update(req.profile_overrides)
        elif req.custom_query and len(req.custom_query.strip()) > 3:
            payload = req.custom_query
        else:
            payload = dict(DEMO_PERSONAS["rameshwar_farmer"])

        if req.draft_grievance and isinstance(payload, dict):
            payload["draft_grievance"] = True

        result = orchestrator.run_agentic_workflow(payload, generate_pdf=True)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow execution error: {str(e)}")


@app.post("/api/grievance")
def generate_grievance(payload: Dict[str, Any] = Body(...)):
    """
    Generates a dedicated formal CPGRAMS / Citizen Charter grievance petition.
    """
    try:
        profile = payload.get("profile", DEMO_PERSONAS["kamala_widow"])
        grievance_info = payload.get("grievance_info")
        petition = orchestrator.grievance_agent.draft_petition(profile, grievance_info)
        return petition
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
def download_pdf(filename: str):
    """
    Serves the minted official application dossier PDF.
    """
    safe_filename = Path(filename).name
    target_path = OUTPUT_DIR / safe_filename
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Requested dossier PDF not found.")
    
    return FileResponse(
        path=str(target_path),
        media_type="application/pdf",
        filename=safe_filename
    )


# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Jan-Sahayak AI API is running. Visit /docs for OpenAPI specs."}


if __name__ == "__main__":
    import uvicorn
    print("Starting Jan-Sahayak Production Server on http://127.0.0.1:8000 ...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
