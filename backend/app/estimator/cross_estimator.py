from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP import Stern
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP.bjmm import BJMM
from math import inf


def estimate_stern(n: int, k: int):
    """Ejecuta Stern con todos los ell probados."""
    problem = CROSSProblem(n=n, k=k)
    stern = Stern(problem, bit_complexities=1)
    
    results = []
    best_time = inf
    best_ell = None
    
    for params in stern._valid_choices():
        ell = params["ell"]
        
        try:
            time, memory = stern._time_and_memory_complexity(params)
            
            if time != inf and time > 0:
                results.append({
                    "ell": ell,
                    "time": round(time, 2),
                    "memory": round(memory, 2),
                })
                
                if time < best_time:
                    best_memory = memory
                    best_time = time
                    best_ell = ell
        except:
            continue
    
    return {
        "algorithm": "Stern",
        "n": n,
        "k": k,
        "n-k": n - k,
        "optimal": {
            "ell": best_ell,
            "time": round(best_time, 2) if best_time != inf else None,
            "memory": round(best_memory, 2) if best_memory != inf else None,
        },
        "data": results,  # Para graficar: x=ell, y=time
    }


def estimate_bjmm(n: int, k: int):
    """Ejecuta BJMM con todos los parámetros probados (limitado a mejores por ell para graficar)."""
    problem = CROSSProblem(n=n, k=k)
    bjmm = BJMM(problem, bit_complexities=1)
    
    results = []
    best_time = inf
    best_params = None
    
    # Recorrer parámetros válidos
    for params in bjmm._valid_choices():
        ell = params["ell"]
        
        try:
            time, memory = bjmm._time_and_memory_complexity(params)
            
            if time != inf and time > 0:
                results.append({
                    "ell": ell,
                    "nu1": params["nu1"],
                    "nu2": params["nu2"],
                    "delta1": params["delta1"],
                    "delta2": params["delta2"],
                    "time": round(time, 2),
                    "memory": round(memory, 2),
                })
                
                if time < best_time:
                    best_time = time
                    best_memory = memory
                    best_params = {
                        "ell": ell,
                        "nu1": params["nu1"],
                        "nu2": params["nu2"],
                        "delta1": params["delta1"],
                        "delta2": params["delta2"],
                    }
        except:
            continue
    
    # Mejor tiempo por cada ell (para graficar)
    best_by_ell = {}
    for item in results:
        ell = item["ell"]
        if ell not in best_by_ell or item["time"] < best_by_ell[ell]["time"]:
            best_by_ell[ell] = item
    
    return {
        "algorithm": "BJMM",
        "n": n,
        "k": k,
        "n-k": n - k,
        "optimal": {
            "ell": best_params["ell"] if best_params else None,
            "nu1": best_params["nu1"] if best_params else None,
            "nu2": best_params["nu2"] if best_params else None,
            "delta1": best_params["delta1"] if best_params else None,
            "delta2": best_params["delta2"] if best_params else None,
            "time": round(best_time, 2) if best_time != inf else None,
            "memory": round(best_memory, 2) if best_memory != inf else None,
        },
        "data": list(best_by_ell.values()),  # Para graficar: x=ell, y=time
    }