"""
Authentication endpoints (stub - to be implemented)
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def auth_status():
    """Check auth status"""
    return {"status": "auth_stub", "message": "Authentication endpoints coming soon"}
