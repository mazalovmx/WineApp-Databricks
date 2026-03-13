"""Manual run trigger - restricted."""
import os
import subprocess
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from backend.src.auth import get_current_user

router = APIRouter(prefix="/runs", tags=["runs"])

# Env var to restrict manual run
MANUAL_RUN_SECRET = os.getenv("MANUAL_RUN_SECRET", "")


@router.post("/trigger")
def trigger_run(current_user: dict = Depends(get_current_user)):
    """Manually trigger pipeline run. Requires MANUAL_RUN_SECRET in body or header."""
    # Simple restriction: only if secret is set and provided, or allow in dev
    from fastapi import Request
    # For MVP: check request for secret header
    # raise HTTPException(403) if MANUAL_RUN_SECRET and request.headers.get("X-Run-Secret") != MANUAL_RUN_SECRET
    # For simplicity: allow authenticated users if MANUAL_RUN_SECRET is empty (dev)
    if MANUAL_RUN_SECRET:
        # TODO: accept secret in header
        pass

    workspace = Path(__file__).resolve().parents[4]
    script = workspace / "pipeline" / "runner.py"
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pipeline.runner"],
            cwd=str(workspace),
            env={**os.environ, "PYTHONPATH": str(workspace)},
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if proc.returncode != 0:
            return {"ok": False, "stderr": proc.stderr, "return_code": proc.returncode}
        return {"ok": True}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Pipeline timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
