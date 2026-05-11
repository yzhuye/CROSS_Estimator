from cryptographic_estimators.base_algorithm import BaseAlgorithm
from .cross_problem import CROSSProblem
from .cross_constants import VerboseInformation
from .cross_helper import min_max
from math import log2, inf


class CROSSAlgorithm(BaseAlgorithm):
    """
    Clase base para todos los algoritmos de ataque a CROSS R-SDP.
    
    Extiende BaseAlgorithm con funcionalidades específicas para
    el problema R-SDP (Restricted Syndrome Decoding Problem).
    
    Args:
        problem (CROSSProblem): Objeto con los parámetros del problema.
        **kwargs: Argumentos adicionales para BaseAlgorithm.
    """
    
    def __init__(self, problem: CROSSProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self._name = "CROSSAlgorithm"
        
        # Inicializar el parámetro r para eliminación Gaussiana M4RI
        if "r" not in self._optimal_parameters:
            self._optimal_parameters["r"] = 0
    
    @property
    def n(self):
        """Longitud del código N."""
        return self.problem.n
    
    @property
    def k(self):
        """Dimensión del código K."""
        return self.problem.k
    
    @property
    def p(self):
        """Característica del cuerpo finito."""
        return self.problem.p
    
    @property
    def z(self):
        """Orden del subgrupo E."""
        return self.problem.z
    
    @property
    def z_D(self):
        """Tamaño del conjunto auxiliar D."""
        return self.problem.z_D
    
    @property
    def alpha_E(self):
        """Aditividad de E."""
        return self.problem.alpha_E
    
    @property
    def alpha_D(self):
        """Aditividad de D."""
        return self.problem.alpha_D
    
    @property
    def full_domain(self):
        """
        Indica si se debe buscar en el dominio completo.
        
        Returns:
            bool: True para búsqueda completa.
        """
        return True
    
    def _gaussian_elimination_complexity(self):
        """
        Complejidad de eliminación Gaussiana para R-SDP sobre Fp.
        
        Returns:
            float: log2 del coste de eliminación Gaussiana.
        """
        from .cross_helper import gaussian_elimination_complexity_rsdp
        n, k, p = self.problem.n, self.problem.k, self.problem.p
        cost = gaussian_elimination_complexity_rsdp(n, k, p)
        return log2(cost) if cost > 0 else 0
    
    def _is_early_abort_possible(self, amount):
        """
        Verifica si se puede realizar un aborto temprano de la optimización.
        
        Args:
            amount (float): Cantidad a verificar.
            
        Returns:
            bool: True si se debe abortar.
        """
        return amount > 500  # Límite práctico
    
    @property
    def _adjust_radius(self):
        """
        Radio de ajuste para búsqueda de parámetros.
        
        Returns:
            int: Radio de búsqueda.
        """
        return 10
    
    def _compute_time_complexity(self, parameters: dict):
        """
        Sobrescribe el método de BaseAlgorithm.
        Redirige a _time_and_memory_complexity y retorna solo el tiempo.
        
        Args:
            parameters (dict): Parámetros de la instancia.
            
        Returns:
            float: Complejidad temporal.
        """
        time, _ = self._time_and_memory_complexity(parameters)
        return time
    
    def _compute_memory_complexity(self, parameters: dict):
        """
        Sobrescribe el método de BaseAlgorithm.
        Redirige a _time_and_memory_complexity y retorna solo la memoria.
        
        Args:
            parameters (dict): Parámetros de la instancia.
            
        Returns:
            float: Complejidad de memoria.
        """
        _, memory = self._time_and_memory_complexity(parameters)
        return memory
    
    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        """
        Método a implementar por las subclases.
        Calcula tiempo y memoria juntos para eficiencia.
        
        Args:
            parameters (dict): Parámetros de la instancia.
            verbose_information (dict, optional): Información de depuración.
            
        Returns:
            tuple: (time_complexity, memory_complexity)
            
        Raises:
            NotImplementedError: Si la subclase no implementa este método.
        """
        raise NotImplementedError("Subclasses must implement _time_and_memory_complexity")
    
    def __repr__(self):
        return f"{self._name} estimator for CROSS R-SDP with {self.problem}"