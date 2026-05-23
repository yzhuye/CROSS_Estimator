from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP import Stern
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP.bjmm import BJMM
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDPG import Stern_G
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

def estimate_groebner(n: int, k: int, z: int = 7, omega: float = 2.0):
    """Ejecuta el estimador Gröbner (F5) sobre R-SDP. Sin parámetros optimizables."""
    from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.groebner import Groebner
    problem = CROSSProblem(n=n, k=k, z=z)
    groebner = Groebner(problem, omega=omega, bit_complexities=1)

    verbose_info = {}
    params = next(groebner._valid_choices())
    try:
        time, memory = groebner._time_and_memory_complexity(params, verbose_information=verbose_info)
    except Exception:
        time, memory = inf, inf

    return {
        "algorithm": "Groebner",
        "n": n,
        "k": k,
        "z": z,
        "omega": omega,
        "optimal": {
            "d_reg":  verbose_info.get("d_reg"),
            "time":   round(time,   2) if time   != inf else None,
            "memory": round(memory, 2) if memory != inf else None,
        },
    }


def estimate_collision_search(n: int, k: int, m: int, z: int = 127, p: int = 509):
    """Ejecuta Submatrix Stern/Dumer (Teorema 15) sobre R-SDP(G).

    Optimiza sobre (ja, jb, da, db). Validación: NIST-1 debe dar tiempo en [2^143.1, 2^144.5].
    """
    from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDPG import CollisionSearch

    problem = CROSSProblem(n=n, k=k, z=z, p=p, m=m)
    algo = CollisionSearch(problem, bit_complexities=1)

    best_time   = inf
    best_memory = inf
    best_params = None

    for params in algo._valid_choices():
        try:
            time, memory = algo._time_and_memory_complexity(params)
            if time < best_time and time != inf:
                best_time   = time
                best_memory = memory
                best_params = dict(params)
        except Exception:
            continue

    return {
        "algorithm": "CollisionSearch",
        "n": n, "k": k, "m": m, "z": z,
        "optimal": {
            "ja":    best_params["ja"]  if best_params else None,
            "jb":    best_params["jb"]  if best_params else None,
            "da":    best_params["da"]  if best_params else None,
            "db":    best_params["db"]  if best_params else None,
            "rho_a": best_params["ja"] - best_params["da"] if best_params else None,
            "rho_b": best_params["jb"] - best_params["db"] if best_params else None,
            "time":   round(best_time,   2) if best_time   != inf else None,
            "memory": round(best_memory, 2) if best_memory != inf else None,
        },
    }


def estimate_stern_g(n: int, k: int, m: int, z: int = 127, p: int = 509):
    """Ejecuta Stern_G sobre R-SDP(G). Itera sobre ell y retorna el óptimo."""
    problem = CROSSProblem(n=n, k=k, z=z, p=p, m=m)
    stern_g = Stern_G(problem, bit_complexities=1)

    results = []
    best_time = inf
    best_ell = None
    best_memory = inf

    for params in stern_g._valid_choices():
        ell = params.get("ell", 0)
        try:
            time, memory = stern_g._time_and_memory_complexity(params)
            if time != inf and time > 0:
                results.append({"ell": ell, "time": round(time, 2), "memory": round(memory, 2)})
                if time < best_time:
                    best_time = time
                    best_memory = memory
                    best_ell = ell
        except Exception:
            continue

    return {
        "algorithm": "Stern_G",
        "n": n,
        "k": k,
        "m": m,
        "z": z,
        "optimal": {
            "ell":    best_ell,
            "time":   round(best_time,   2) if best_time   != inf else None,
            "memory": round(best_memory, 2) if best_memory != inf else None,
        },
        "data": results,
    }