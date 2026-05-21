from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms import Groebner

for cat, (n, k) in [("Cat 1", (127, 76)), ("Cat 3", (187, 111)), ("Cat 5", (251, 150))]:
    g = Groebner(CROSSProblem(n=n, k=k), bit_complexities=1)
    print(f"{cat}: λ_Gröbner = {g.time_complexity():.1f} bits, "
          f"memoria = {g.memory_complexity():.1f} bits")