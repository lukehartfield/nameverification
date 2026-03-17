"""FastAPI app for the name verification take-home."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.generator import generate as generate_name
from backend.store import get_latest_target_name, set_latest_target_name
from backend.verifier import verify as verify_name


class GenerateRequest(BaseModel):
    prompt: str


class VerifyRequest(BaseModel):
    candidate: str


app = FastAPI(title="Name Verification App")

FRONTEND_INDEX = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


@app.get("/")
def read_index() -> FileResponse:
    """Serve the single-page frontend."""
    return FileResponse(FRONTEND_INDEX)


@app.get("/status")
def read_status() -> dict:
    """Return the latest generated target name, if any."""
    return {"target_name": get_latest_target_name()}


@app.post("/generate")
def generate_target(payload: GenerateRequest) -> dict:
    """Generate and persist the latest target name string."""
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")

    generated_name = generate_name(prompt)
    set_latest_target_name(generated_name)
    return {"name": generated_name}


@app.post("/verify")
def verify_candidate(payload: VerifyRequest) -> dict:
    """Verify a candidate name against the latest generated target string."""
    candidate = payload.candidate.strip()
    if not candidate:
        raise HTTPException(status_code=400, detail="Candidate name is required.")

    latest_target_name = get_latest_target_name()
    if latest_target_name is None:
        raise HTTPException(
            status_code=409,
            detail="No target name generated yet. Generate a target name first.",
        )

    return verify_name(latest_target_name, candidate)
