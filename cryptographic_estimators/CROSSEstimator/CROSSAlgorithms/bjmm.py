from ..cross_algorithm import CROSSAlgorithm
from cryptographic_estimators.base_algorithm import optimal_parameter
from types import SimpleNamespace
from math import log2, inf, comb
from ..cross_constants import VerboseInformation
from ..cross_helper import min_max


class BJMM(CROSSAlgorithm):
    """
    Implementación del ataque BJMM de 4 niveles para CROSS R-SDP.
    
    Basado en la Sección 2 del paper de CROSS.
    
    Parámetros de optimización:
        ell (int): Tamaño del filtro.
        nu1 (int): Solapamientos E nivel 1→0.
        nu2 (int): Solapamientos E nivel 2→1.
        delta1 (int): Solapamientos D nivel 1→0.
        delta2 (int): Solapamientos D nivel 2→1.
        
    Args:
        problem (CROSSProblem): Objeto con los parámetros del problema.
        **kwargs: Argumentos adicionales.
    """
    
    def __init__(self, problem, **kwargs):
        self._name = "BJMM"
        super().__init__(problem, **kwargs)
        self.initialize_parameter_ranges()
    
    def initialize_parameter_ranges(self):
        """
        Inicializa los rangos de parámetros para la optimización.
        """
        n, k = self.problem.n, self.problem.k
        s = self.full_domain
        
        self.set_parameter_ranges("ell", 0, min_max(n - k, 60, s))
        self.set_parameter_ranges("nu1", 0, 10)
        self.set_parameter_ranges("nu2", 0, 10)
        self.set_parameter_ranges("delta1", 0, 10)
        self.set_parameter_ranges("delta2", 0, 10)
    
    @optimal_parameter
    def ell(self):
        return self._get_optimal_parameter("ell")
    
    @optimal_parameter
    def nu1(self):
        return self._get_optimal_parameter("nu1")
    
    @optimal_parameter
    def nu2(self):
        return self._get_optimal_parameter("nu2")
    
    @optimal_parameter
    def delta1(self):
        return self._get_optimal_parameter("delta1")
    
    @optimal_parameter
    def delta2(self):
        return self._get_optimal_parameter("delta2")
    
    @optimal_parameter
    def r(self):
        return self._get_optimal_parameter("r")
    
    def _calcular_niveles(self, ell, nu1, nu2, delta1, delta2):
        """
        Calcula los parámetros de cada nivel según relaciones (12)-(14).
        """
        v0 = (self.k + ell) // 2
        d0 = (self.k + ell) // 2
        v1 = v0
        d1 = 0
        v2 = 2 * (v1 - nu1)
        d2 = 2 * (v1 // 2 - nu1 - delta1)
        v3 = 2 * (v2 - nu2)
        d3 = 2 * (v2 // 2 - nu2 - delta2)
        
        return v0, d0, v1, d1, v2, d2, v3, d3
    
    def _lema_11(self, v_i, d_i, v_ip1, d_ip1, nu, delta):
        """
        Implementa el Lema 11 del paper CROSS (fórmula 19).
        """
        alpha_E = self.problem.alpha_E
        alpha_D = self.problem.alpha_D
        
        # Validaciones
        if v_i < 0 or d_i < 0 or v_ip1 < 0 or d_ip1 < 0 or nu < 0 or delta < 0:
            return 0
        
        if v_i < v_ip1 or v_ip1 < 2 * nu or v_i // 2 - nu < delta or d_i < d_i // 2:
            return 0
        
        factor1 = comb(v_i, v_ip1)
        factor2 = comb(v_ip1, 2 * nu) * alpha_E**(2 * nu)
        factor3 = comb(v_i // 2 - nu, delta)**2 * alpha_D**(2 * delta)
        factor4 = comb(d_i, d_i // 2)
        
        return factor1 * factor2 * factor3 * factor4
    
    def _are_parameters_invalid(self, parameters: dict):
        """
        Verifica si los parámetros son inválidos.
        """
        n, k = self.problem.n, self.problem.k
        par = SimpleNamespace(**parameters)
        
        if par.ell < 0 or par.ell > n - k:
            return True
        
        if (k + par.ell) % 2 != 0:
            return True
        
        v0, d0, v1, d1, v2, d2, v3, d3 = self._calcular_niveles(
            par.ell, par.nu1, par.nu2, par.delta1, par.delta2
        )
        
        if any(x < 0 for x in [v1, d1, v2, d2, v3, d3]):
            return True
        
        return False
    
    def _valid_choices(self):
        """
        Generador de combinaciones válidas de parámetros.
        
        NOTA: Con 5 parámetros la búsqueda exhaustiva es muy costosa.
        Se recomienda fijar algunos parámetros con set_parameters().
        """
        new_ranges = self._fix_ranges_for_already_set_parameters()
        
        for ell in range(
            new_ranges["ell"]["min"],
            new_ranges["ell"]["max"] + 1,
            2
        ):
            for nu1 in range(new_ranges["nu1"]["min"], new_ranges["nu1"]["max"] + 1):
                for nu2 in range(new_ranges["nu2"]["min"], new_ranges["nu2"]["max"] + 1):
                    for delta1 in range(new_ranges["delta1"]["min"], new_ranges["delta1"]["max"] + 1):
                        for delta2 in range(new_ranges["delta2"]["min"], new_ranges["delta2"]["max"] + 1):
                            indices = {
                                "ell": ell,
                                "nu1": nu1,
                                "nu2": nu2,
                                "delta1": delta1,
                                "delta2": delta2,
                                "r": self._optimal_parameters["r"],
                            }
                            if self._are_parameters_invalid(indices):
                                continue
                            yield indices
    
    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        """
        Calcula la complejidad temporal y de memoria para BJMM.
        
        Fórmula (15) del paper CROSS.
        """
        n, k, p, z, z_D, alpha_E, alpha_D = self.problem.get_parameters()
        par = SimpleNamespace(**parameters)
        
        memory_bound = self.problem.memory_bound
        
        # Calcular parámetros de niveles
        v0, d0, v1, d1, v2, d2, v3, d3 = self._calcular_niveles(
            par.ell, par.nu1, par.nu2, par.delta1, par.delta2
        )
        
        # Validación adicional
        if any(x < 0 for x in [v1, d1, v2, d2, v3, d3]):
            return inf, inf
        
        # Tamaños de listas
        L3 = z**v3 * z_D**d3
        L2 = z**v2 * z_D**d2
        L1 = z**v1 * z_D**d1
        
        if self._is_early_abort_possible(log2(max(L1, L2, L3))):
            return inf, inf
        
        # Memoria (máximo de las listas)
        max_level = max(
            log2(L3 * (v3 * log2(z) + d3 * log2(z_D))),
            log2(L2 * (v2 * log2(z) + d2 * log2(z_D))),
            log2(L1 * (v1 * log2(z) + d1 * log2(z_D)))
        )
        memory = max_level
        
        if memory > memory_bound:
            return inf, memory_bound + 1
        
        # Coste Gaussiano
        T_gauss = self._gaussian_elimination_complexity()
        
        # Estimación de ell1, ell0 (simplificada)
        ell1 = par.ell // 3 if par.ell > 0 else 0
        ell0 = par.ell // 3 if par.ell > 0 else 0
        
        # Nivel 3: Construcción de listas base (fórmula 23)
        T3 = log2(2 * L3 * (ell1 * log2(p) + v3 * log2(z) + d3 * log2(z_D)))
        
        # Nivel 2: Concatenación merge (fórmula 24)
        T2 = log2(2 * L2 * (ell0 * log2(p) + v2 * log2(z) + d2 * log2(z_D)))
        
        # Nivel 1: Representación merge (fórmula 25)
        T1 = log2(2 * L2**2 * p**(-ell0) * log2(p)) if L2 > 0 and ell0 > 0 else 0
        
        # Nivel 0: Solución final (fórmula 26)
        rem = par.ell - ell0 - ell1
        T0 = log2(L1**2 * p**(-rem) * log2(p)) if L1 > 0 and rem > 0 else 0
        
        # Coste total por iteración
        T_iter = log2(2**T_gauss + 2**T3 + 2**T2 + 2**T1 + 2**T0)
        
        # Ajuste por memoria
        mem_cost = self.memory_access_cost(memory)
        T_iter_adj = T_iter + mem_cost
        
        # Probabilidad de éxito (fórmula 18)
        r1 = self._lema_11(v0, d0, v1, d1, par.nu1, par.delta1)
        r0 = self._lema_11(v1, d1, v2, d2, par.nu2, par.delta2)
        
        P = (r1 * r0) / z**(k + par.ell) if r1 > 0 and r0 > 0 else 1e-10
        
        # Coste total ajustado por probabilidad
        nsolutions = self.problem.expected_number_solutions()
        time = T_iter_adj - log2(max(1, P)) - nsolutions
        
        if verbose_information is not None:
            verbose_information[VerboseInformation.GAUSS.value] = T_gauss
            verbose_information[VerboseInformation.LISTS.value] = [
                log2(L3) if L3 > 0 else 0,
                log2(L2) if L2 > 0 else 0,
                log2(L1) if L1 > 0 else 0,
            ]
            verbose_information[VerboseInformation.REPRESENTATIONS.value] = {
                "ell": par.ell,
                "P_log2": log2(P) if P > 0 else float('-inf'),
            }
        
        return time, memory
    
    def __repr__(self):
        return f"BJMM estimator for CROSS R-SDP with {self.problem}"