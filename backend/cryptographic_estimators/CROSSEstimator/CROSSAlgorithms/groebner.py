from ..cross_algorithm import CROSSAlgorithm
from cryptographic_estimators.base_algorithm import optimal_parameter
from math import log2, inf
from ..cross_helper import binom_log2, log2_safe


# ──────────────────────────────────────────────────────────────────────
# Modelo del grado de regularidad (STUB inicial)
# ──────────────────────────────────────────────────────────────────────

def _d_reg_model(n: int, k: int, w: int, z: int, c: float) -> int:
    """
    Modelo del grado de regularidad para el sistema polinomial de R-SDP.

    STUB: d_reg = round(c * n).
    Será reemplazado por la función ajustada experimentalmente mediante
    regresión sobre datos de MAGMA/SageMath (ver experiments/groebner/).

    Args:
        n (int): Longitud del código.
        k (int): Dimensión del código.
        w (int): Peso del vector de error.
        z (int): Orden del subgrupo cíclico E.
        c (float): Coeficiente lineal (a calibrar).

    Returns:
        int: d_reg estimado.
    """
    return max(1, round(c * n))


# ──────────────────────────────────────────────────────────────────────
# Clase estimadora
# ──────────────────────────────────────────────────────────────────────

class Groebner(CROSSAlgorithm):
    """
    Estimador del ataque por bases de Gröbner (F4/F5) sobre R-SDP.

    Complejidad asintótica (Sección 7.2 de la especificación CROSS v1.2):

        T_Gröbner = C(n + d_reg, d_reg)^omega · log2(p)   [ops. binarias]
        M_Gröbner = C(n + d_reg, d_reg)^2     · log2(p)   [bits]

    donde d_reg es el grado de regularidad del sistema polinomial asociado
    a la instancia R-SDP. A diferencia de los ataques ISD (Stern, BJMM),
    este algoritmo es determinista y no tiene parámetros de diseño
    optimizables por el atacante.

    Args:
        problem (CROSSProblem): Parámetros del problema R-SDP.
        omega (float): Exponente de multiplicación matricial.
            - 2.00 → cota inferior teórica (default, conservadora para el defensor).
            - 2.81 → Strassen (implementable en la práctica).
            - 2.37 → Coppersmith-Winograd (límite teórico asintótico).
        c (float): Coeficiente del modelo stub d_reg = c·n.
            Reemplazar por el valor ajustado experimentalmente.
        **kwargs: Argumentos adicionales para la clase base.

    References:
        [1] Faugère, J.C.: A new efficient algorithm for computing Gröbner
            bases without reduction to zero (F5). ISSAC 2002.
        [2] CROSS Team: CROSS Specification v1.2, Section 7.2, 2023.
        [3] Bardet, M., Faugère, J.C., Salvy, B.: On the complexity of the
            F5 Gröbner basis algorithm. JSC, 2015.
    """

    def __init__(self, problem, omega: float = 2.0, c: float = 0.1, **kwargs):
        self._omega = omega
        self._c = c
        super().__init__(problem, **kwargs)
        self._name = "Groebner"         
        self.initialize_parameter_ranges()

    def initialize_parameter_ranges(self):
        """Sin parámetros optimizables en el ataque de Gröbner."""
        pass

    @optimal_parameter
    def r(self):
        """Parámetro r heredado del framework (no relevante en Gröbner)."""
        return self._get_optimal_parameter("r")

    def _are_parameters_invalid(self, parameters: dict) -> bool:
        return False

    def _valid_choices(self):
        """Gröbner es determinista: yieldea un único conjunto de parámetros."""
        yield {"r": self._optimal_parameters.get("r", 0)}

    def _compute_memory(self, d_reg: int, n: int, p: int) -> float:
        """
        Memoria para la matriz de Macaulay en grado d_reg.

            M = C(n + d_reg, d_reg)^2 · log2(p)   [bits]
            log2(M) = 2 · log2(C(n + d_reg, d_reg)) + log2(log2(p))

        Args:
            d_reg (int): Grado de regularidad.
            n (int): Longitud del código.
            p (int): Característica del cuerpo.

        Returns:
            float: log2 de la memoria requerida en bits.
        """
        log2_N = binom_log2(n + d_reg, d_reg)
        return 2 * log2_N + log2_safe(log2(p))

    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        """
        Complejidad temporal y de memoria del ataque de Gröbner sobre R-SDP.

        Args:
            parameters (dict): Ignorado (Gröbner no tiene parámetros optimizables).
            verbose_information (dict, optional): Si se provee, se añaden los
                valores intermedios d_reg, log2_N y omega.

        Returns:
            tuple[float, float]: (log2_tiempo, log2_memoria) en bits.
        """
        n, k, p, z, _, _, _ = self.problem.get_parameters()

        # R-SDP estándar: peso completo
        w = n

        # Grado de regularidad (STUB: reemplazar con modelo ajustado experimentalmente)
        d_reg = _d_reg_model(n, k, w, z, self._c)

        if d_reg <= 0:
            return inf, inf

        # N = C(n + d_reg, d_reg)  →  número de monomios en grado ≤ d_reg, n variables
        log2_N = binom_log2(n + d_reg, d_reg)

        if log2_N <= 0:
            return inf, inf

        # T = N^omega · log2(p)
        log2_time = self._omega * log2_N + log2_safe(log2(p))

        # M = N^2 · log2(p)
        log2_memory = self._compute_memory(d_reg, n, p)

        if log2_memory > self.problem.memory_bound:
            return inf, self.problem.memory_bound + 1

        if verbose_information is not None:
            verbose_information["d_reg"]  = d_reg
            verbose_information["log2_N"] = log2_N
            verbose_information["omega"]  = self._omega

        return log2_time, log2_memory

    def __repr__(self):
        return (
            f"Gröbner estimator for CROSS R-SDP with {self.problem} "
            f"[omega={self._omega}, d_reg stub: c={self._c}]"
        )