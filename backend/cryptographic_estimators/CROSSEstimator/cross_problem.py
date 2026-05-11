from cryptographic_estimators.base_problem import BaseProblem
from math import log2
from .cross_constants import CROSSDefaults


class CROSSProblem(BaseProblem):
    """
    Problema R-SDP (Restricted Syndrome Decoding Problem) para CROSS.
    
    Instancia: Dados:
        - Un número primo p y un elemento g ∈ Fp* de orden primo z.
        - El subgrupo cíclico E = {g^i | i ∈ {1, ..., z}} ⊂ Fp*.
        - Una matriz de paridad H ∈ Fp^{(n-k)×n}.
        - Un síndrome s ∈ Fp^{n-k}.
    
    Objetivo: Encontrar un vector e ∈ E^n tal que e·H^T = s.

    Args:
        n (int): Longitud del código.
        k (int): Dimensión del código.
        p (int, opcional): Característica del cuerpo finito. Por defecto 127.
        z (int, opcional): Orden del subgrupo E. Por defecto 7.
        z_D (int, opcional): Tamaño del conjunto auxiliar D. Por defecto 35.
        alpha_E (int, opcional): Aditividad de E. Por defecto 1.
        alpha_D (int, opcional): Aditividad de D. Por defecto 5.
        memory_bound (float, opcional): Límite máximo de memoria. Por defecto inf.
    
    Examples:
        >>> from cryptographic_estimators.CROSSEstimator import CROSSProblem
        >>> CROSSProblem(n=127, k=76)
        CROSSProblem(n=127, k=76, p=127, z=7)
    """
    
    def __init__(self, n: int, k: int, 
                 p: int = CROSSDefaults.P,
                 z: int = CROSSDefaults.Z,
                 z_D: int = CROSSDefaults.Z_D,
                 alpha_E: int = CROSSDefaults.ALPHA_E,
                 alpha_D: int = CROSSDefaults.ALPHA_D,
                 **kwargs):
        
        super().__init__(**kwargs)
        
        # Parámetros del código
        self.n = n
        self.k = k
        
        # Parámetros del cuerpo finito y subgrupos
        self.p = p
        self.z = z
        self.z_D = z_D
        self.alpha_E = alpha_E
        self.alpha_D = alpha_D
        
        # Número esperado de soluciones (fórmula 10 del paper CROSS)
        # N_sol = z^n * p^{-(n-k)}
        # Para instancias de CROSS, esto es ≤ 1 por diseño
        nsolutions = z**n * p**(-(n - k))
        self._nsolutions = max(1.0, nsolutions)
    
    def to_bitcomplexity_time(self, basic_operations: float) -> float:
        """
        Convierte operaciones básicas a complejidad en bits.
        
        Para R-SDP sobre Fp, una operación básica es una operación en Fp,
        que tiene un coste aproximado de log2(p) bits.
        
        Args:
            basic_operations (float): Número de operaciones básicas (en log2).
            
        Returns:
            float: Complejidad en bits.
        """
        return basic_operations + log2(log2(self.p))
    
    def to_bitcomplexity_memory(self, elements_to_store: float) -> float:
        """
        Convierte elementos a almacenar a complejidad de memoria en bits.
        
        Cada elemento en Fp ocupa log2(p) bits.
        
        Args:
            elements_to_store (float): Número de elementos (en log2).
            
        Returns:
            float: Complejidad de memoria en bits.
        """
        return elements_to_store + log2(log2(self.p))
    
    def expected_number_solutions(self) -> float:
        """
        Retorna el número esperado de soluciones.
        
        Returns:
            float: Logaritmo del número esperado de soluciones.
        """
        return log2(self._nsolutions)
    
    def get_parameters(self):
        """
        Retorna los parámetros del problema.
        
        Returns:
            tuple: (n, k, p, z, z_D, alpha_E, alpha_D)
        """
        return (self.n, self.k, self.p, self.z, self.z_D, self.alpha_E, self.alpha_D)
    
    def __repr__(self):
        return f"CROSSProblem(n={self.n}, k={self.k}, p={self.p}, z={self.z})"