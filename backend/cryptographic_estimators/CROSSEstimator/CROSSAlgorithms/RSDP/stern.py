from ...cross_algorithm import CROSSAlgorithm
from cryptographic_estimators.base_algorithm import optimal_parameter
from types import SimpleNamespace
from math import log2, inf
from ...cross_constants import VerboseInformation
from ...cross_helper import min_max


class Stern(CROSSAlgorithm):
    """
    Implementación del ataque Stern/Dumer para CROSS R-SDP.
    """
    
    def __init__(self, problem, **kwargs):
        self._name = "Stern"
        super().__init__(problem, **kwargs)
        self.initialize_parameter_ranges()
    
    def initialize_parameter_ranges(self):
        n, k = self.problem.n, self.problem.k
        s = self.full_domain
        self.set_parameter_ranges("ell", 0, min_max(n - k, 100, s))
    
    @optimal_parameter
    def ell(self):
        return self._get_optimal_parameter("ell")
    
    @optimal_parameter
    def r(self):
        return self._get_optimal_parameter("r")
    
    def _are_parameters_invalid(self, parameters: dict):
        n, k = self.problem.n, self.problem.k
        ell = parameters.get("ell", 0)
        
        if ell < 2 or ell > n - k:
            return True
        if (k + ell) % 2 != 0:
            return True
        return False
    
    def _valid_choices(self):
        """Generador de parámetros válidos - ACCESO DIRECTO A RANGOS"""
        min_ell = self._parameter_ranges["ell"]["min"]
        max_ell = self._parameter_ranges["ell"]["max"]
        k = self.k
        
        # Ajustar paridad: k + ell debe ser PAR
        if (k + min_ell) % 2 != 0:
            min_ell += 1
        
        # Mínimo práctico: ell >= 2
        if min_ell < 2:
            min_ell = 2
            if (k + min_ell) % 2 != 0:
                min_ell += 1
        
        for ell in range(min_ell, max_ell + 1, 2):
            yield {"ell": ell, "r": self._optimal_parameters.get("r", 0)}
    
    def _compute_memory(self, parameters: dict):
        n, k, p, z, _, _, _, _ = self.problem.get_parameters()
        ell = parameters.get("ell", 0)
        half = (k + ell) // 2
        
        L = z**half
        if L <= 0:
            return 0.0
        
        mem = L * (half * log2(z) + ell * log2(p))
        return log2(mem) if mem > 0 else 0.0
    
    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        n, k, p, z, _, _, _, _ = self.problem.get_parameters()
        ell = parameters.get("ell", 0)
        half = (k + ell) // 2
        
        memory_bound = self.problem.memory_bound
        
        L = z**half
        if L <= 0:
            return inf, inf
        
        logL = log2(L)
        if self._is_early_abort_possible(logL):
            return inf, inf
        
        memory = self._compute_memory(parameters)
        if memory > memory_bound:
            return inf, memory_bound + 1
        
        # Componentes del coste
        T_gauss = self._gaussian_elimination_complexity()
        
        # T_build
        bc = 2 * L * (half * log2(z) + ell * log2(p))
        T_build = log2(bc) if bc > 0 else 0
        
        # T_match
        if logL > 0 and ell > 0:
            mc = 2 * L * logL * ell * log2(p)
            T_match = log2(mc) if mc > 0 else 0
        else:
            T_match = 0
        
        # T_verify
        if ell > 0:
            N_cand = L**2 * p**(-ell)
            vc = N_cand * (k + ell) * log2(p) if N_cand > 0 else 0
            T_verify = log2(vc) if vc > 0 else 0
        else:
            T_verify = 0
        
        # Suma en espacio logarítmico
        parts = []
        for v in [T_gauss, T_build, T_match, T_verify]:
            if v > 0:
                parts.append(2**v)
        
        T_iter = log2(sum(parts)) if parts else 0
        T_iter_adj = T_iter + self.memory_access_cost(memory)
        time = T_iter_adj - self.problem.expected_number_solutions()
        
        return time, memory
    
    def __repr__(self):
        return f"Stern estimator for CROSS R-SDP with {self.problem}"