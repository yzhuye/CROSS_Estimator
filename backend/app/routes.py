from fastapi import APIRouter
from app.schemas import CrossRequest
from app.service import analyze_stern, analyze_bjmm

router = APIRouter()

@router.post("/cross/stern")
def cross_stern(data: CrossRequest):
    """Estima seguridad con ataque Stern."""
    return analyze_stern(data.n, data.k)

@router.post("/cross/bjmm")
def cross_bjmm(data: CrossRequest):
    """Estima seguridad con ataque BJMM."""
    return analyze_bjmm(data.n, data.k)