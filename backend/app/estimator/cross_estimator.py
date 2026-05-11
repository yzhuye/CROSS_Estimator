from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms import Stern

def estimate_cross(n: int, k: int):
    problem = CROSSProblem(n=n, k=k)

    stern = Stern(problem, bit_complexities=1)

    return {
    "time": stern.time_complexity(),
    "memory": stern.memory_complexity(),
    "l": stern.ell()
}