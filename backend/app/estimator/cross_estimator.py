from cryptographic_estimators.CROSSEstimator import CROSSProblem
from backend.cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP import Stern
from backend.cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP.bjmm import BJMM


def estimate_stern(n: int, k: int):
    """Ejecuta solo Stern."""
    problem = CROSSProblem(n=n, k=k)
    stern = Stern(problem, bit_complexities=1)
    
    return {
        "algorithm": "Stern",
        "n": n, "k": k, "n-k": n - k,
        "time": round(stern.time_complexity(), 1),
        "memory": round(stern.memory_complexity(), 1),
        "ell": stern.ell(),
    }


def estimate_bjmm(n: int, k: int):
    """Ejecuta solo BJMM."""
    problem = CROSSProblem(n=n, k=k)
    bjmm = BJMM(problem, bit_complexities=1)
    
    return {
        "algorithm": "BJMM",
        "n": n, "k": k, "n-k": n - k,
        "time": round(bjmm.time_complexity(), 1),
        "memory": round(bjmm.memory_complexity(), 1),
        "ell": bjmm.ell(),
        "nu1": bjmm.nu1(),
        "nu2": bjmm.nu2(),
        "delta1": bjmm.delta1(),
        "delta2": bjmm.delta2(),
    }