from cryptographic_estimators.base_estimator import BaseEstimator
from .cross_algorithm import CROSSAlgorithm
from .cross_problem import CROSSProblem


class CROSSEstimator(BaseEstimator):
    """
    Estimador para el criptosistema CROSS.
    
    Evalúa la seguridad de CROSS contra ataques ISD:
        - Stern/Dumer
        - BJMM (4 niveles)
    
    Args:
        n (int): Longitud del código.
        k (int): Dimensión del código.
        p (int, opcional): Característica del cuerpo. Por defecto 127.
        z (int, opcional): Orden del subgrupo. Por defecto 7.
        z_D (int, opcional): Tamaño del conjunto auxiliar. Por defecto 35.
        alpha_E (int, opcional): Aditividad de E. Por defecto 1.
        alpha_D (int, opcional): Aditividad de D. Por defecto 5.
        **kwargs: Argumentos adicionales para BaseEstimator.
        
    Examples:
        >>> from cryptographic_estimators.CROSSEstimator import CROSSEstimator
        >>> A = CROSSEstimator(n=127, k=76)
        >>> A.table(precision=1)
    """
    
    def __init__(self, n: int, k: int, 
                 p: int = 127, z: int = 7,
                 z_D: int = 35, alpha_E: int = 1, alpha_D: int = 5,
                 **kwargs):
        
        problem = CROSSProblem(
            n=n, k=k, p=p, z=z, z_D=z_D,
            alpha_E=alpha_E, alpha_D=alpha_D,
            **{k: v for k, v in kwargs.items() if k in ['memory_bound']}
        )
        
        estimator_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['memory_bound']}
        
        super().__init__(CROSSAlgorithm, problem, **estimator_kwargs)
    
    def __repr__(self):
        return f"CROSSEstimator(n={self.problem.n}, k={self.problem.k})"