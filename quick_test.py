from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms import Stern

for name, n, k in [("Cat.1", 127, 76), ("Cat.3", 187, 111), ("Cat.5", 251, 150)]:
    problem = CROSSProblem(n=n, k=k)
    stern = Stern(problem, bit_complexities=1)
    time_cx = stern.time_complexity()
    memory = stern.memory_complexity()
    ell = stern.ell()
    
    print(f"\n{name}: n={n}, k={k}")
    print(f"  Tiempo: {time_cx:.1f} bits")
    print(f"  Memoria: {memory:.1f} bits")
    print(f"  ℓ óptimo: {ell}")