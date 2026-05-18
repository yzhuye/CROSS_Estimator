from ..cross_algorithm import CROSSAlgorithm
from cryptographic_estimators.base_algorithm import optimal_parameter
from math import log2, inf, lgamma, log
from ..cross_constants import VerboseInformation
from ..cross_helper import min_max

def _log2_binom(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -float('inf')
    if k == 0 or k == n:
        return 0.0
    return (lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)) / log(2)

def _log2_multinomial(n: int, a: int, b: int) -> float:
    c = n - a - b
    if c < 0:
        return -float('inf')
    return (lgamma(n + 1) - lgamma(a + 1) - lgamma(b + 1) - lgamma(c + 1)) / log(2)


class BJMM(CROSSAlgorithm):
    """
    Implementación del ataque BJMM/REPR para CROSS R-SDP.

    Parámetros libres: ell, nu1, nu2, delta1, delta2
    Los demás (v0,v1,v2,v3,d1,d2,d3) se derivan según el paper.
    """

    def __init__(self, problem, **kwargs):
        self._name = "BJMM"
        super().__init__(problem, **kwargs)
        self.initialize_parameter_ranges()

    def initialize_parameter_ranges(self):
        n, k = self.problem.n, self.problem.k
        s = self.full_domain
        max_ell = min_max(n - k, 100, s)
        max_nu = n // 4
        max_delta = n // 4
        self.set_parameter_ranges("ell",     2,       max_ell)
        self.set_parameter_ranges("nu1",     0,       max_nu)
        self.set_parameter_ranges("nu2",     0,       max_nu)
        self.set_parameter_ranges("delta1",  0,       max_delta)
        self.set_parameter_ranges("delta2",  0,       max_delta)

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

    def _derive_params(self, ell, nu1, nu2, delta1, delta2):
        """
        Deriva los parámetros estructurales a partir de los 5 libres.

        Del paper (sección 3.1.2):
            v0 = k + ell
            v1 = v0/2 + nu1
            v2 = v1/2 + nu2
            v3 = v2/2
            d1 = delta1          (= d0/2 + delta1, con d0=0)
            d2 = d1/2 + delta2
            d3 = d2/2
        """
        k = self.k
        v0 = k + ell
        v1 = v0 // 2 + nu1
        v2 = v1 // 2 + nu2
        v3 = v2 // 2
        d1 = delta1
        d2 = d1 // 2 + delta2
        d3 = d2 // 2
        return v0, v1, v2, v3, d1, d2, d3

    def _are_parameters_invalid(self, parameters: dict):
        n, k = self.problem.n, self.problem.k
        ell    = parameters.get("ell",    0)
        nu1    = parameters.get("nu1",    0)
        nu2    = parameters.get("nu2",    0)
        delta1 = parameters.get("delta1", 0)
        delta2 = parameters.get("delta2", 0)

        # rango básico
        if ell < 2 or ell > n - k:
            return True

        # k+ell par (necesario para v0/2 entero)
        if (k + ell) % 2 != 0:
            return True

        v0, v1, v2, v3, d1, d2, d3 = self._derive_params(
            ell, nu1, nu2, delta1, delta2
        )

        # paridad de v1 (necesario para v1/2 entero)
        if v1 % 2 != 0:
            return True

        # paridad de v2 (necesario para v3=v2/2 entero)
        if v2 % 2 != 0:
            return True

        # paridad de d1 (necesario para d1/2 entero)
        if d1 % 2 != 0:
            return True

        # paridad de d2 (necesario para d3=d2/2 entero)
        if d2 % 2 != 0:
            return True

        # no negatividad
        if nu1 < 0 or nu2 < 0 or delta1 < 0 or delta2 < 0:
            return True

        # orden natural de v
        if not (0 <= v3 <= v2 <= v1 <= v0):
            return True

        # condiciones del Lema 9
        # nivel 0->1: C(v0/2 - nu1, delta1) debe ser válido
        if v0 // 2 - nu1 < delta1:
            return True

        # nivel 1->2: C(v1/2 - nu2, delta2) debe ser válido
        if v1 // 2 - nu2 < delta2:
            return True

        # listas base no vacías
        half = (k + ell) // 2
        if v3 + d3 > half:
            return True
        if v2 + d2 > k + ell:
            return True
        if v1 + d1 > k + ell:
            return True

        return False

    def _valid_choices(self):
        """
        Búsqueda en 2 fases para reducir tiempo sin perder precisión.
        
        Fase 1: Paso grueso (step=3 para nu1,nu2; step=4 para delta1; step=3 para delta2)
        Fase 2: Paso fino alrededor del mejor de Fase 1
        """
        new_ranges = self._fix_ranges_for_already_set_parameters()
        k = self.k

        min_ell = max(2, new_ranges["ell"]["min"])
        max_ell = new_ranges["ell"]["max"]
        if (k + min_ell) % 2 != 0:
            min_ell += 1

        # Determinar si estamos en Fase 1 o Fase 2
        already_has_ell = "ell" in self._optimal_parameters and self._optimal_parameters["ell"] is not None
        
        if not already_has_ell:
            # ============================================================
            # FASE 1: Búsqueda gruesa con pasos grandes
            # ============================================================
            step_nu = 3
            step_delta1 = 4
            step_delta2 = 3
            
            for ell in range(min_ell, max_ell + 1, 4):  # paso 4 en ell
                v0 = k + ell
                v0h = v0 // 2
                nu1_start = v0h % 2

                for nu1 in range(nu1_start, new_ranges["nu1"]["max"] + 1, max(2, step_nu)):
                    v1 = v0h + nu1
                    v1h = v1 // 2
                    nu2_start = v1h % 2

                    for nu2 in range(nu2_start, new_ranges["nu2"]["max"] + 1, max(2, step_nu)):
                        
                        for delta1 in range(0, new_ranges["delta1"]["max"] + 1, max(2, step_delta1)):
                            d1h = delta1 // 2
                            delta2_start = d1h % 2

                            for delta2 in range(delta2_start, new_ranges["delta2"]["max"] + 1, max(2, step_delta2)):
                                params = {
                                    "ell": ell, "nu1": nu1, "nu2": nu2,
                                    "delta1": delta1, "delta2": delta2,
                                    "r": self._optimal_parameters.get("r", 0),
                                }
                                if not self._are_parameters_invalid(params):
                                    yield params
        else:
            # ============================================================
            # FASE 2: Refinamiento alrededor del óptimo de Fase 1
            # ============================================================
            best_ell = self._optimal_parameters.get("ell", min_ell)
            best_nu1 = self._optimal_parameters.get("nu1", 0)
            best_nu2 = self._optimal_parameters.get("nu2", 0)
            best_delta1 = self._optimal_parameters.get("delta1", 0)
            best_delta2 = self._optimal_parameters.get("delta2", 0)
            
            # Ventana de búsqueda alrededor del óptimo
            ell_range = range(max(min_ell, best_ell - 6), min(max_ell, best_ell + 7), 2)
            nu1_range = range(max(0, best_nu1 - 4), min(new_ranges["nu1"]["max"], best_nu1 + 5))
            nu2_range = range(max(0, best_nu2 - 4), min(new_ranges["nu2"]["max"], best_nu2 + 5))
            delta1_range = range(max(0, best_delta1 - 4), min(new_ranges["delta1"]["max"], best_delta1 + 5), 2)
            delta2_range = range(max(0, best_delta2 - 4), min(new_ranges["delta2"]["max"], best_delta2 + 5))
            
            for ell in ell_range:
                v0 = k + ell
                v0h = v0 // 2
                nu1_start = v0h % 2

                for nu1 in nu1_range:
                    if nu1 < nu1_start or (nu1 - nu1_start) % 2 != 0:
                        # Ajustar paridad
                        if nu1 % 2 != nu1_start % 2:
                            continue
                    v1 = v0h + nu1
                    v1h = v1 // 2
                    nu2_start = v1h % 2

                    for nu2 in nu2_range:
                        if nu2 < nu2_start or (nu2 - nu2_start) % 2 != 0:
                            if nu2 % 2 != nu2_start % 2:
                                continue
                        
                        for delta1 in delta1_range:
                            d1h = delta1 // 2
                            delta2_start = d1h % 2

                            for delta2 in delta2_range:
                                if delta2 < delta2_start or (delta2 - delta2_start) % 2 != 0:
                                    if delta2 % 2 != delta2_start % 2:
                                        continue
                                
                                params = {
                                    "ell": ell, "nu1": nu1, "nu2": nu2,
                                    "delta1": delta1, "delta2": delta2,
                                    "r": self._optimal_parameters.get("r", 0),
                                }
                                if not self._are_parameters_invalid(params):
                                    yield params

    def _compute_memory(self, parameters: dict):
        n, k, p, z, z_D, alpha_E, alpha_D = self.problem.get_parameters()
        ell    = parameters.get("ell",    0)
        nu1    = parameters.get("nu1",    0)
        nu2    = parameters.get("nu2",    0)
        delta1 = parameters.get("delta1", 0)
        delta2 = parameters.get("delta2", 0)

        v0, v1, v2, v3, d1, d2, d3 = self._derive_params(
            ell, nu1, nu2, delta1, delta2
        )

        L    = k + ell
        half = L // 2
        logp = log2(p)

        # calcular ell1 y ell0 aquí directamente
        log_r1 = (_log2_binom(v1, v2)
                + _log2_binom(v2, 2 * nu2)
                + 2 * nu2 * log2(alpha_E)
                + 2 * _log2_binom(v1 // 2 - nu2, delta2)
                + 2 * delta2 * log2(alpha_D)
                + _log2_binom(d1, d1 // 2))

        log_r0 = (_log2_binom(v0, v1)
                + _log2_binom(v1, 2 * nu1)
                + 2 * nu1 * log2(alpha_E)
                + 2 * _log2_binom(v0 // 2 - nu1, delta1)
                + 2 * delta1 * log2(alpha_D))

        ell1 = max(0.0, log_r1 / logp)
        ell0 = max(0.0, log_r0 / logp - ell1)

        log_L3 = (_log2_multinomial(half, v3, d3)
                + v3 * log2(z) + d3 * log2(z_D))
        log_L2 = (_log2_multinomial(L, v2, d2)
                + v2 * log2(z) + d2 * log2(z_D)
                - ell1 * logp)
        log_L1 = (_log2_multinomial(L, v1, d1)
                + v1 * log2(z) + d1 * log2(z_D)
                - (ell0 + ell1) * logp)

        return max(log_L3, log_L2, log_L1)


    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        n, k, p, z, z_D, alpha_E, alpha_D = self.problem.get_parameters()
        ell    = parameters.get("ell",    0)
        nu1    = parameters.get("nu1",    0)
        nu2    = parameters.get("nu2",    0)
        delta1 = parameters.get("delta1", 0)
        delta2 = parameters.get("delta2", 0)

        v0, v1, v2, v3, d1, d2, d3 = self._derive_params(
            ell, nu1, nu2, delta1, delta2
        )

        L    = k + ell
        half = L // 2
        logp = log2(p)
        memory_bound = self.problem.memory_bound

        # --- calcular r1, r0, ell1, ell0 una sola vez ---
        log_r1 = (_log2_binom(v1, v2)
                + _log2_binom(v2, 2 * nu2)
                + 2 * nu2 * log2(alpha_E)
                + 2 * _log2_binom(v1 // 2 - nu2, delta2)
                + 2 * delta2 * log2(alpha_D)
                + _log2_binom(d1, d1 // 2))

        log_r0 = (_log2_binom(v0, v1)
                + _log2_binom(v1, 2 * nu1)
                + 2 * nu1 * log2(alpha_E)
                + 2 * _log2_binom(v0 // 2 - nu1, delta1)
                + 2 * delta1 * log2(alpha_D))

        if log_r1 < 0 or log_r0 < 0:
            return inf, inf

        ell1    = log_r1 / logp
        ell0    = max(0.0, log_r0 / logp - ell1)
        ell_rem = ell - ell0 - ell1

        if ell1 <= 0 or ell0 <= 0 or ell_rem <= 0:
            return inf, inf

        # --- tamaños de listas ---
        log_L3 = (_log2_multinomial(half, v3, d3)
                + v3 * log2(z) + d3 * log2(z_D))
        log_L2 = (_log2_multinomial(L, v2, d2)
                + v2 * log2(z) + d2 * log2(z_D)
                - ell1 * logp)
        log_L1 = (_log2_multinomial(L, v1, d1)
                + v1 * log2(z) + d1 * log2(z_D)
                - (ell0 + ell1) * logp)

        if min(log_L3, log_L2, log_L1) < 0:
            return inf, inf

        memory = max(log_L3, log_L2, log_L1)

        if self._is_early_abort_possible(memory):
            return inf, inf

        if memory > memory_bound:
            return inf, memory_bound + 1

        # --- costes por nivel (Teorema 10) ---
        bits3  = ell1 * logp + v3 * log2(z) + d3 * log2(z_D)
        log_C3 = 1 + log_L3 + log2(max(bits3, 1e-300))

        bits2  = ell0 * logp + v2 * log2(z) + d2 * log2(z_D)
        log_C2 = 1 + log_L2 + log2(max(bits2, 1e-300))

        log_C1 = 1 + 2 * log_L2 - ell0 * logp + log2(logp)
        log_C0 = 2 * log_L1 - ell_rem * logp + log2(logp)

        # suma en espacio logarítmico
        costs = [log_C3, log_C2, log_C1, log_C0]
        max_c = max(costs)
        log_total = max_c + log2(sum(2 ** (c - max_c) for c in costs))

        log_total += self.memory_access_cost(memory)
        log_total -= max(0.0, self.problem.expected_number_solutions())

        if verbose_information is not None:
            verbose_information[VerboseInformation.CONSTRAINTS.value] = {
                "ell": ell, "v0": v0, "v1": v1, "v2": v2, "v3": v3,
                "d1": d1, "d2": d2, "d3": d3,
                "ell1": round(ell1, 2), "ell0": round(ell0, 2),
                "ell_rem": round(ell_rem, 2),
            }

        return log_total, memory

    def __repr__(self):
        return f"BJMM estimator for CROSS R-SDP with {self.problem}"