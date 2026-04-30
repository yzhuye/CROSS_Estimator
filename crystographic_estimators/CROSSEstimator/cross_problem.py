"""
Definición del problema CROSS
"""

from base_problem import BaseProblem
from math import log2, comb
from .cross_constants import *

class CROSSProblem(BaseProblem):
    """
    Problema criptográfico de CROSS
    
    CROSS basa su seguridad en:
    - RSDP: Regular Syndrome Decoding Problem
    - RSDPG: RSDP with Gaussian elimination
    
    Parámetros:
    - n: longitud del código
    - k: dimensión del código  
    - w: peso del error (número de coordenadas no cero)
    - t: peso de los vectores de restricción (z)
    - m: parámetro adicional para RSDPG (opcional)
    """
    
    def __init__(self, n, k, w, t, m=None, variant='RSDP', lambda_=128, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.k = k
        self.w = w
        self.t = t
        self.m = m
        self.variant = variant.upper()
        self.lambda_ = lambda_
        
        # Validar parámetros según la variante
        if self.variant == 'RSDPG' and m is None:
            raise ValueError("RSDPG variant requires parameter 'm'")
            
        # Dimensiones del código dual
        self.n_minus_k = n - k
        
    @property
    def code_rate(self):
        """Tasa del código R = k/n"""
        return self.k / self.n
    
    @property
    def error_weight(self):
        """Peso del error relativo"""
        return self.w / self.n
    
    def expected_solutions(self):
        """
        Número esperado de soluciones al problema RSDP
        Considerando la estructura regular del error
        """
        # En RSDP, el error tiene exactamente w coordenadas no cero
        # y cada coordenada tiene una estructura específica
        return comb(self.n, self.w)
    
    def to_bit_complexity(self, time_complexity, memory_complexity=None):
        """
        Convierte complejidad a bits de seguridad
        """
        if time_complexity == float('inf'):
            return float('inf')
        return log2(time_complexity)
    
    def get_parameters(self):
        """Retorna diccionario con parámetros del problema"""
        params = {
            'n': self.n,
            'k': self.k,
            'w': self.w,
            't': self.t,
            'variant': self.variant
        }
        if self.variant == 'RSDPG':
            params['m'] = self.m
        return params
    
    def __str__(self):
        return f"CROSS-{self.variant}(n={self.n}, k={self.k}, w={self.w}, t={self.t})"