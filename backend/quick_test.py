from cryptographic_estimators.CROSSEstimator.cross_problem import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDPG.stern import Stern_G

# R-SDP(G) - NIST Category 1 (Tabla 3)
problem = CROSSProblem(n=55, k=36, m=25)

stern_g = Stern_G(problem)
time = stern_g.time_complexity()
memory = stern_g.memory_complexity()

print(f"Stern_G - R-SDP(G) NIST 1")
print(f"  Tiempo:  {time:.2f} bits")
print(f"  Memoria: {memory:.2f} bits")
print(f"  ell:     {stern_g.ell()}")