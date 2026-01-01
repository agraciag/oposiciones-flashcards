"""
Legislation updates endpoints (stub - to be implemented)
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def legislation_status():
    """Check legislation updates status"""
    return {"status": "legislation_stub", "message": "Legislation tracking endpoints coming soon"}
