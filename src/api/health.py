from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def general():
    """General health check endpoint"""
    return {"status": "healthy", "service": "octowalrus"} 