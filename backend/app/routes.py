from fastapi import APIRouter
from app.schemas import CrossRequest, RSDPGRequest
from app.service import analyze_stern, analyze_bjmm, analyze_groebner, analyze_stern_g

router = APIRouter()

@router.post("/cross/stern")
def cross_stern(data: CrossRequest):
    """Estima seguridad con ataque Stern."""
    return analyze_stern(data.n, data.k)

@router.post("/cross/bjmm")
def cross_bjmm(data: CrossRequest):
    """Estima seguridad con ataque BJMM."""
    return analyze_bjmm(data.n, data.k)

@router.post("/cross/groebner")
def cross_groebner(data: CrossRequest):
    """Estima seguridad con ataque Gröbner basis (F5) sobre R-SDP."""
    return analyze_groebner(data.n, data.k, data.z)

@router.post("/rsdpg/stern")
def rsdpg_stern(data: RSDPGRequest):
    """Estima seguridad con Stern sobre R-SDP(G) (ignora estructura de G)."""
    return analyze_stern_g(data.n, data.k, data.m, data.z, data.p)