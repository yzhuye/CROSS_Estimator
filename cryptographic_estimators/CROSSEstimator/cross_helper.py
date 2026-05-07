from math import log2, comb


def min_max(a: int, b: int, s: bool) -> int:
    """
    Returns the minimum or maximum of two integers based on a boolean switch.

    Args:
        a (int): The first integer.
        b (int): The second integer.
        s (bool): If True, returns max(a,b). If False, returns min(a,b).

    Returns:
        int: The minimum or maximum of a and b.
    """
    if a > b:
        return a if s else b
    return b if s else a


def log2_safe(x: float) -> float:
    """
    Calcula log2 de forma segura, evitando log(0).
    
    Args:
        x (float): Valor a calcular.
        
    Returns:
        float: log2(x) o 0 si x <= 0.
    """
    if x <= 0:
        return 0.0
    return log2(x)


def binom_log2(n: int, k: int) -> float:
    """
    Calcula el logaritmo en base 2 del coeficiente binomial C(n, k).
    
    Args:
        n (int): Parámetro superior.
        k (int): Parámetro inferior.
        
    Returns:
        float: log2(C(n, k)).
    """
    if k < 0 or k > n:
        return 0.0
    if k == 0 or k == n:
        return 0.0
    
    # Usar la fórmula: log2(C(n,k)) = sum_{i=1}^k log2(n-k+i) - sum_{i=1}^k log2(i)
    result = 0.0
    for i in range(1, min(k, n - k) + 1):
        result += log2(n - k + i) - log2(i)
    return result


def trinomial_log2(n: int, v: int, d: int) -> float:
    """
    Calcula el logaritmo del coeficiente trinomial: n! / (v! * d! * (n-v-d)!)
    
    Args:
        n (int): Total.
        v (int): Número de entradas tipo v.
        d (int): Número de entradas tipo d.
        
    Returns:
        float: log2 del coeficiente trinomial.
    """
    remaining = n - v - d
    if remaining < 0 or v < 0 or d < 0:
        return 0.0
    
    # log2( n! / (v! * d! * (n-v-d)!) )
    # = sum_{i=1}^n log2(i) - sum_{i=1}^v log2(i) - sum_{i=1}^d log2(i) - sum_{i=1}^{remaining} log2(i)
    result = 0.0
    for i in range(1, n + 1):
        result += log2(i)
    for i in range(1, v + 1):
        result -= log2(i)
    for i in range(1, d + 1):
        result -= log2(i)
    for i in range(1, remaining + 1):
        result -= log2(i)
    return result


def gaussian_elimination_complexity_rsdp(n: int, k: int, p: int) -> float:
    """
    Complejidad de eliminación Gaussiana para R-SDP sobre Fp.
    
    Fórmula (3) del paper CROSS:
    T_Gauss = (n-k)^ω · n · log2(p)
    
    Args:
        n (int): Longitud del código.
        k (int): Dimensión del código.
        p (int): Característica del cuerpo.
        
    Returns:
        float: Coste de la eliminación Gaussiana.
    """
    omega = 2.8  # Exponente de multiplicación de matrices
    return (n - k)**omega * n * log2(p)


def list_build_complexity_rsdp(L: float, half: int, ell: int, p: int, z: int) -> float:
    """
    Complejidad de construcción de listas para R-SDP.
    
    Fórmula (4) del paper CROSS.
    
    Args:
        L (float): Tamaño de la lista.
        half (int): (k+ℓ)/2.
        ell (int): Tamaño del filtro.
        p (int): Característica del cuerpo.
        z (int): Orden del subgrupo.
        
    Returns:
        float: Coste de construcción.
    """
    return 2 * L * (half * log2(z) + ell * log2(p))


def list_merge_complexity_rsdp(L: float, ell: int, p: int) -> float:
    """
    Complejidad de búsqueda de colisiones para R-SDP.
    
    Fórmula (5) del paper CROSS.
    
    Args:
        L (float): Tamaño de la lista.
        ell (int): Tamaño del filtro.
        p (int): Característica del cuerpo.
        
    Returns:
        float: Coste de búsqueda de colisiones.
    """
    return 2 * L * log2(L) * ell * log2(p)


def verify_complexity_rsdp(L: float, ell: int, k: int, p: int) -> float:
    """
    Complejidad de verificación de candidatos para R-SDP.
    
    Fórmula (6) del paper CROSS.
    
    Args:
        L (float): Tamaño de la lista.
        ell (int): Tamaño del filtro.
        k (int): Dimensión del código.
        p (int): Característica del cuerpo.
        
    Returns:
        float: Coste de verificación.
    """
    N_cand = L**2 * p**(-ell)
    return N_cand * (k + ell) * log2(p)