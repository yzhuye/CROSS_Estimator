from fastapi import APIRouter
from app.schemas import CrossRequest
from app.service import analyze_cross

router = APIRouter()

@router.post("/cross")
def cross_estimation(data: CrossRequest):
    return analyze_cross(data)