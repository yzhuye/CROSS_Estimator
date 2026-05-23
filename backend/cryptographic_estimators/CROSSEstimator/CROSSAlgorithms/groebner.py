from ..cross_algorithm import CROSSAlgorithm
from cryptographic_estimators.base_algorithm import optimal_parameter
from math import log2, log, inf
from pathlib import Path
import json
import warnings
from ..cross_helper import binom_log2, log2_safe


# ──────────────────────────────────────────────────────────────────────
# Modelo del grado de regularidad (ajustado experimentalmente)
# ──────────────────────────────────────────────────────────────────────

# Ruta del modelo ajustado por analyze_results.py
_MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "experiments" / "groebner" / "models" / "d_reg_model.json"
)

# Caché del modelo (lazy loading, una sola vez por proceso)
_FITTED_MODEL = None
_FITTED_MODEL_LOADED = False


def _load_fitted_model():
    """Carga el modelo ajustado desde JSON con caché. Returns None si no existe."""
    global _FITTED_MODEL, _FITTED_MODEL_LOADED
    if _FITTED_MODEL_LOADED:
        return _FITTED_MODEL

    _FITTED_MODEL_LOADED = True
    if not _MODEL_PATH.exists():
        warnings.warn(
            f"No se encontró modelo ajustado en {_MODEL_PATH}. "
            "Usando stub d_reg = c·n. Corre experiments/groebner/analyze_results.py primero.",
            RuntimeWarning,
            stacklevel=3,
        )
        return None

    with open(_MODEL_PATH) as f:
        _FITTED_MODEL = json.load(f)
    return _FITTED_MODEL


def _d_reg_model(n: int, k: int, w: int, z: int, c: float = 1.0) -> int:
    """
    Modelo del grado de regularidad para el sistema polinomial de R-SDP.

    Si existe un modelo ajustado experimentalmente (analyze_results.py), lo usa.
    Si no, recurre al stub `d_reg = c·n`.

    Args:
        n, k, w, z: Parámetros del problema R-SDP.
        c (float): Coeficiente del stub (ignorado si hay modelo ajustado).

    Returns:
        int: d_reg estimado (≥ 1).
    """
    model = _load_fitted_model()

    if model is None:
        return max(1, round(c * n))

    form = model["best_model"]
    a = model["coefficients"]

    if form == "linear":
        # d_reg = a0 + a1·n + a2·k + a3·w + a4·z
        d_reg = a[0] + a[1] * n + a[2] * k + a[3] * w + a[4] * z
    elif form == "logarithmic":
        # d_reg = a0 + a1·n + a2·ln(z) + a3·(n-k)
        d_reg = a[0] + a[1] * n + a[2] * log(z) + a[3] * (n - k)
    elif form == "mixed":
        # d_reg = a0 + a1·n + a2·(n-k) + a3·(w/n) + a4·ln(z)
        d_reg = a[0] + a[1] * n + a[2] * (n - k) + a[3] * (w / n) + a[4] * log(z)
    else:
        raise ValueError(f"Forma de modelo desconocida en JSON: {form}")

    return max(1, round(d_reg))


# ──────────────────────────────────────────────────────────────────────
# Clase estimadora
# ──────────────────────────────────────────────────────────────────────

class Groebner(CROSSAlgorithm):
    """
    Estimador del ataque por bases de Gröbner (F4/F5) sobre R-SDP.

    Complejidad asintótica (CROSS spec v1.2, §7.2):

        T_Gröbner = C(n + d_reg, d_reg)^omega · log2(p)   [ops. binarias]
        M_Gröbner = C(n + d_reg, d_reg)^2     · log2(p)   [bits]

    `d_reg` se obtiene del modelo ajustado experimentalmente sobre 85
    instancias R-SDP (ver experiments/groebner/models/d_reg_model.json).

    Args:
        problem (CROSSProblem): Parámetros del problema R-SDP.
        omega (float): Exponente de multiplicación matricial.
            - 2.00 → cota inferior teórica (default, conservadora).
            - 2.81 → Strassen.
            - 2.37 → Coppersmith-Winograd.
        c (float): Coeficiente del stub d_reg = c·n. Solo se usa si no hay
            modelo ajustado disponible.

    References:
        [1] Faugère: A new efficient algorithm for computing Gröbner bases
            without reduction to zero (F5). ISSAC 2002.
        [2] CROSS Team: CROSS Specification v1.2, Section 7.2, 2023.
        [3] Bardet, Faugère, Salvy: On the complexity of the F5 Gröbner basis
            algorithm. JSC, 2015.
    """

    def __init__(self, problem, omega: float = 2.0, c: float = 1.0, **kwargs):
        self._omega = omega
        self._c = c
        super().__init__(problem, **kwargs)
        self._name = "Groebner"
        self.initialize_parameter_ranges()

    def initialize_parameter_ranges(self):
        """Sin parámetros optimizables en Gröbner."""
        pass

    @optimal_parameter
    def r(self):
        return self._get_optimal_parameter("r")

    def _are_parameters_invalid(self, parameters: dict) -> bool:
        return False

    def _valid_choices(self):
        yield {"r": self._optimal_parameters.get("r", 0)}

    def _compute_memory(self, d_reg: int, n: int, p: int) -> float:
        log2_N = binom_log2(n + d_reg, d_reg)
        return 2 * log2_N + log2_safe(log2(p))

    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        n, k, p, z, _, _, _, _ = self.problem.get_parameters()
        w = n  # R-SDP estándar: peso completo

        d_reg = _d_reg_model(n, k, w, z, self._c)
        if d_reg <= 0:
            return inf, inf

        log2_N = binom_log2(n + d_reg, d_reg)
        if log2_N <= 0:
            return inf, inf

        log2_time = self._omega * log2_N + log2_safe(log2(p))
        log2_memory = self._compute_memory(d_reg, n, p)

        if log2_memory > self.problem.memory_bound:
            return inf, self.problem.memory_bound + 1

        if verbose_information is not None:
            verbose_information["d_reg"]  = d_reg
            verbose_information["log2_N"] = log2_N
            verbose_information["omega"]  = self._omega

        return log2_time, log2_memory

    def __repr__(self):
        m = _load_fitted_model()
        model_info = f"fitted={m['best_model']}" if m else f"stub c={self._c}"
        return (
            f"Gröbner estimator for CROSS R-SDP with {self.problem} "
            f"[omega={self._omega}, {model_info}]"
        )