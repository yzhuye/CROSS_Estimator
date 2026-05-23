from app.estimator.cross_estimator import estimate_stern, estimate_bjmm, estimate_groebner, estimate_stern_g

def analyze_stern(n, k):
    return estimate_stern(n, k)

def analyze_bjmm(n, k):
    return estimate_bjmm(n, k)

def analyze_groebner(n, k, z=7, omega=2.0):
    return estimate_groebner(n, k, z, omega)

def analyze_stern_g(n, k, m, z=127, p=509):
    return estimate_stern_g(n, k, m, z, p)