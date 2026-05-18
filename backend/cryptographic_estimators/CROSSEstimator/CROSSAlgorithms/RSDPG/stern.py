from ...cross_algorithm import CROSSAlgorithm
from cryptographic_estimators.base_algorithm import optimal_parameter
from math import log2, inf
from ...cross_helper import min_max


class Stern_G(CROSSAlgorithm):
    """
    Implementación del ataque Stern/Dumer para CROSS R-SDP(G).
    Basado en Teorema 13 del paper.
    """
    
    def __init__(self, problem, **kwargs):
        self._name = "Stern_G"
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
        min_ell = self._parameter_ranges["ell"]["min"]
        max_ell = self._parameter_ranges["ell"]["max"]
        k = self.k
        
        if (k + min_ell) % 2 != 0:
            min_ell += 1
        
        if min_ell < 2:
            min_ell = 2
            if (k + min_ell) % 2 != 0:
                min_ell += 1
        
        for ell in range(min_ell, max_ell + 1, 2):
            yield {"ell": ell, "r": self._optimal_parameters.get("r", 0)}
    
    def _compute_ell_bar(self, ell: int) -> int:
        """ℓ̄ = max(0, k + ℓ - m)"""
        k = self.problem.k
        m = self.problem.m
        return max(0, k + ell - m)
    
    def _compute_memory(self, parameters: dict):
        """Memoria según Teorema 13: M = L · half · log₂(z)"""
        n, k, p, z, m = self.problem.n, self.problem.k, self.problem.p, self.problem.z, self.problem.m
        ell = parameters.get("ell", 0)
        half = (k + ell) // 2
        
        L = z ** half
        if L <= 0:
            return 0.0
        
        # Solo half * log2(z) (sin el término de p)
        mem = L * half * log2(z)
        return log2(mem) if mem > 0 else 0.0
    
    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        n = self.problem.n
        k = self.problem.k
        p = self.problem.p
        z = self.problem.z
        m = self.problem.m
        
        ell = parameters.get("ell", 0)
        half = (k + ell) // 2
        
        memory_bound = self.problem.memory_bound
        
        L = z ** half
        if L <= 0:
            return inf, inf
        
        logL = log2(L)
        if self._is_early_abort_possible(logL):
            return inf, inf
        
        ell_bar = self._compute_ell_bar(ell)
        
        memory = self._compute_memory(parameters)
        if memory > memory_bound:
            return inf, memory_bound + 1
        
        T_gauss = self._gaussian_elimination_complexity()
        
        # T_build (con dos síndromes)
        build_cost = 2 * L * (half * log2(z) + ell_bar * log2(z) + ell * log2(p))
        T_build = log2(build_cost) if build_cost > 0 else 0
        
        # T_match
        if logL > 0 and (ell_bar + ell) > 0:
            match_cost = 2 * L * logL * (ell_bar * log2(z) + ell * log2(p))
            T_match = log2(match_cost) if match_cost > 0 else 0
        else:
            T_match = 0
        
        # T_verify
        if ell_bar + ell > 0:
            N_cand = (L ** 2) * (z ** (-ell_bar)) * (p ** (-ell))
            verify_cost = N_cand * (k + ell) * log2(p) if N_cand > 0 else 0
            T_verify = log2(verify_cost) if verify_cost > 0 else 0
        else:
            T_verify = 0
        
        # Sumar costos
        parts = []
        for v in [T_gauss, T_build, T_match, T_verify]:
            if v > 0 and v != inf:
                parts.append(2 ** v)
        
        if not parts:
            return inf, memory
        
        T_iter = log2(sum(parts))
        T_iter_adj = T_iter + self.memory_access_cost(memory)
        
        # Número esperado de soluciones (usa m)
        exp_solutions = 1 + (z ** m - 1) * (p ** (k - n))
        time = T_iter_adj - log2(exp_solutions) if exp_solutions > 0 else T_iter_adj
        
        return time, memory
    
    def __repr__(self):
        return f"Stern_G estimator for CROSS R-SDP(G) with {self.problem}"