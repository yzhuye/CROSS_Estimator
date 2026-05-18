from cryptographic_estimators.base_problem import BaseProblem
from math import log2
from .cross_constants import CROSSDefaults


class CROSSProblem(BaseProblem):
    """
    Problema R-SDP (Restricted Syndrome Decoding Problem) para CROSS.
    
    Para R-SDP(G) (subgrupo), se debe proporcionar el parámetro m.
    
    Args:
        n (int): Longitud del código.
        k (int): Dimensión del código.
        p (int, opcional): Característica del cuerpo finito. Por defecto 127.
        z (int, opcional): Orden del subgrupo E. Por defecto 7.
        m (int, opcional): Tamaño del subgrupo G. Si es None, se asume R-SDP (m=n).
        z_D (int, opcional): Tamaño del conjunto auxiliar D. Por defecto 35.
        alpha_E (int, opcional): Aditividad de E. Por defecto 1.
        alpha_D (int, opcional): Aditividad de D. Por defecto 5.
        memory_bound (float, opcional): Límite máximo de memoria. Por defecto inf.
    """
    
    def __init__(self, n: int, k: int, 
                 p: int = None,
                 z: int = None,
                 m: int = None,
                 z_D: int = CROSSDefaults.Z_D,
                 alpha_E: int = CROSSDefaults.ALPHA_E,
                 alpha_D: int = CROSSDefaults.ALPHA_D,
                 **kwargs):
        
        super().__init__(**kwargs)
        
        self.n = n
        self.k = k
        self.m = m if m is not None else n
        
        # Detectar automáticamente p y z según el tipo de problema
        if p is None and z is None:
            if self.m != self.n:  # R-SDP(G)
                self.p = 509
                self.z = 127
            else:  # R-SDP normal
                self.p = 127
                self.z = 7
        else:
            self.p = p if p is not None else 127
            self.z = z if z is not None else 7
        
        self.z_D = z_D
        self.alpha_E = alpha_E
        self.alpha_D = alpha_D
        
        # Número esperado de soluciones (usa m)
        nsolutions = self.z ** self.m * self.p ** (-(n - k))
        self._nsolutions = max(1.0, nsolutions)
    
    def to_bitcomplexity_time(self, basic_operations: float) -> float:
        """Convierte operaciones básicas a complejidad en bits."""
        return basic_operations + log2(log2(self.p))
    
    def to_bitcomplexity_memory(self, elements_to_store: float) -> float:
        """Convierte elementos a almacenar a complejidad de memoria en bits."""
        return elements_to_store + log2(log2(self.p))
    
    def expected_number_solutions(self) -> float:
        """Retorna el logaritmo del número esperado de soluciones."""
        return log2(self._nsolutions)
    
    def get_parameters(self):
        """
        Retorna los parámetros del problema.
        
        Returns:
            tuple: (n, k, p, z, m, z_D, alpha_E, alpha_D)
        """
        return (self.n, self.k, self.p, self.z, self.m, self.z_D, self.alpha_E, self.alpha_D)
    
    def is_rsdpg(self) -> bool:
        """Retorna True si es un problema R-SDP(G) (con subgrupo)."""
        return self.m != self.n
    
    def __repr__(self):
        if self.is_rsdpg():
            return f"CROSSProblem(n={self.n}, k={self.k}, p={self.p}, z={self.z}, m={self.m})"
        return f"CROSSProblem(n={self.n}, k={self.k}, p={self.p}, z={self.z})"