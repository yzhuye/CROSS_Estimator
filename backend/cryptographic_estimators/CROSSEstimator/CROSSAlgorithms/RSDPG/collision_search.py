from ...cross_algorithm import CROSSAlgorithm
from ...cross_helper import binom_log2
from math import log2, inf


# ──────────────────────────────────────────────────────────────────────────────
# Auxiliares matemáticos
# ──────────────────────────────────────────────────────────────────────────────

def _log2_gaussian_binom(n: int, d: int, z: int) -> float:
    """log2 del binomio gaussiano [n choose d]_z.

    [n choose d]_z = prod_{i=0}^{d-1} (z^{n-i} - 1) / (z^{d-i} - 1)

    Python maneja enteros grandes nativamente; no hay overflow.
    """
    if d <= 0 or d > n:
        return 0.0
    result = 0.0
    for i in range(d):
        num = z ** (n - i) - 1
        den = z ** (d - i) - 1
        if num <= 0 or den <= 0:
            return 0.0
        result += log2(num) - log2(den)
    return result


def _log2_P(j: int, d: int, n: int, m: int, z: int) -> float:
    """log2 del upper-bound de P(j, d) — probabilidad de existencia de subcódigo.

    P(j,d) <= min{ C(n,j) * (z^d - 1)^{j-d} * [n-m choose d]_z / [n choose d]_z, 1 }

    Retorna min(log_p, 0.0): clipeado en 0 cuando P >= 1.
    Retorna 0.0 en casos degenerados.

    Ref: CROSS Spec v1.2 §7.1.2, Teorema 15; SecurityDetails v2.2 Ejemplo 14.
    """
    if d <= 0 or j <= 0 or d >= j or n - m < d:
        return 0.0  # P garantizada >= 1

    log_binom_nj = binom_log2(n, j)                      # log2 C(n,j) estándar
    zd_minus_1 = z ** d - 1
    if zd_minus_1 <= 0:
        return 0.0
    log_zd_term    = (j - d) * log2(zd_minus_1)          # log2 (z^d-1)^{j-d}
    log_gauss_nm_d = _log2_gaussian_binom(n - m, d, z)   # log2 [n-m choose d]_z
    log_gauss_n_d  = _log2_gaussian_binom(n,     d, z)   # log2 [n   choose d]_z

    log_p = log_binom_nj + log_zd_term + log_gauss_nm_d - log_gauss_n_d
    return min(log_p, 0.0)


def _log_sum_exp(*log_vals) -> float:
    """Suma numéricamente estable en espacio logarítmico.

    Computa log2(sum(2^v)) ignorando valores <= 0 e inf.
    """
    vals = [v for v in log_vals if 0 < v < inf]
    if not vals:
        return 0.0
    m = max(vals)
    return m + log2(sum(2 ** (v - m) for v in vals))


# ──────────────────────────────────────────────────────────────────────────────
# Clase principal
# ──────────────────────────────────────────────────────────────────────────────

class CollisionSearch(CROSSAlgorithm):
    """Submatrix Stern/Dumer sobre R-SDP(G).

    Implementación del Teorema 15, CROSS spec v1.2 §7.1.2.

    Explota la estructura del subgrupo G ⊆ E^n mediante dos subcódigos
    auxiliares del espacio de paridad de M_G. La optimización es sobre
    cuatro parámetros libres: (j_a, j_b, d_a, d_b).

    Parámetros del atacante:
        j_a   tamaño del soporte del subcódigo a
        j_b   tamaño del soporte del subcódigo b (disjunto de J_a)
        d_a   dimensión del subcódigo a  (1 <= d_a < j_a)
        d_b   dimensión del subcódigo b  (1 <= d_b < j_b)

    Cantidades derivadas:
        rho_a = j_a - d_a   log_z |L_a|
        rho_b = j_b - d_b   log_z |L_b|
        ell   = j_a + j_b - k   altura del filtro en F_p
        ell_t = max(0, rho_a + rho_b - m)   altura del filtro en F_z

    Validación (Example 16, CROSS Spec §8.2):
        NIST-1 R-SDP(G): n=55, k=36, m=25, p=509, z=127
        Óptimo: j_a=19, d_a=1, j_b=23, d_b=4
        Target tiempo: [2^143.1, 2^144.5]
    """

    def __init__(self, problem, **kwargs):
        if not problem.is_rsdpg():
            raise ValueError(
                "CollisionSearch requiere R-SDP(G): use CROSSProblem con m < n. "
                "Para R-SDP puro use Stern o BJMM."
            )
        self._name = "CollisionSearch"
        super().__init__(problem, **kwargs)
        self.initialize_parameter_ranges()

    def initialize_parameter_ranges(self):
        pass  # iteración manual en _valid_choices()

    def _are_parameters_invalid(self, parameters: dict) -> bool:
        n, k, p, z, m, _, _, _ = self.problem.get_parameters()
        ja = parameters.get("ja", 0)
        jb = parameters.get("jb", 0)
        da = parameters.get("da", 0)
        db = parameters.get("db", 0)

        if da < 1 or db < 1:
            return True
        if da >= ja or db >= jb:        # rho_a, rho_b >= 1
            return True
        if ja + jb > n:                 # soportes caben en el código
            return True
        ell = ja + jb - k
        if ell <= 0 or ell > n - k:    # filtro positivo y válido
            return True
        return False

    def _valid_choices(self):
        """Generador de parámetros (ja, jb, da, db) válidos.

        Por simetría se impone ja <= jb (intercambiar ja/jb da el mismo costo).
        Se acota da, db <= 8 para los parámetros CROSS conocidos (óptimo da=1,db=4).
        """
        n, k, p, z, m, _, _, _ = self.problem.get_parameters()
        max_d = 8   # los parámetros óptimos NIST son siempre d_a,d_b <= 6

        for ja in range(1, n // 2 + 2):
            for jb in range(ja, n - ja + 1):
                ell = ja + jb - k
                if ell <= 0:
                    continue
                if ell > n - k:
                    break
                for da in range(1, min(ja, max_d + 1)):
                    for db in range(1, min(jb, max_d + 1)):
                        yield {"ja": ja, "jb": jb, "da": da, "db": db}

    def _compute_memory(self, ja, jb, da, db, log2z) -> float:
        """log2 de la memoria en bits (cota inferior).

        M >= min(|L_a|*rho_a, |L_b|*rho_b) * log2(z)
        log2(M) = min(rho_a*log2z + log2(rho_a*log2z),
                      rho_b*log2z + log2(rho_b*log2z))
        """
        rho_a = ja - da
        rho_b = jb - db
        bits_a = rho_a * log2z
        bits_b = rho_b * log2z
        if bits_a <= 0 or bits_b <= 0:
            return 0.0
        log_mem_a = rho_a * log2z + log2(bits_a)
        log_mem_b = rho_b * log2z + log2(bits_b)
        return min(log_mem_a, log_mem_b)

    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        """Complejidad temporal y de memoria del Teorema 15.

        Fórmula:
            C >= A + B
            A = (C_iter / N_sol) * log2(M)   [iteración interna]
            B = 1 / (P(j_a,d_a) * P(j_b,d_b))   [búsqueda de subcódigo]

        Retorna (time, memory) en escala log2 de bits.
        """
        if self._are_parameters_invalid(parameters):
            return inf, inf

        n, k, p, z, m, _, _, _ = self.problem.get_parameters()
        ja = parameters["ja"]
        jb = parameters["jb"]
        da = parameters["da"]
        db = parameters["db"]

        rho_a = ja - da
        rho_b = jb - db
        ell   = ja + jb - k
        ell_t = max(0, rho_a + rho_b - m)

        log2z = log2(z)
        log2p = log2(p)

        # ── Abort temprano ────────────────────────────────────────────────────
        if self._is_early_abort_possible(rho_a * log2z):
            return inf, inf
        if self._is_early_abort_possible(rho_b * log2z):
            return inf, inf

        # ── Memoria ───────────────────────────────────────────────────────────
        memory = self._compute_memory(ja, jb, da, db, log2z)
        if memory <= 0:
            return inf, inf

        memory_bound = self.problem.memory_bound
        if memory > memory_bound:
            return inf, memory_bound + 1

        # ── C_a: costo de construir L_a ───────────────────────────────────────
        per_elem_a = rho_a * log2z + ell_t * log2z + ell * log2p
        if per_elem_a <= 0:
            return inf, inf
        log_Ca = rho_a * log2z + log2(per_elem_a)

        # ── C_b: costo de construir L_b ───────────────────────────────────────
        per_elem_b = rho_b * log2z + ell_t * log2z + ell * log2p
        if per_elem_b <= 0:
            return inf, inf
        log_Cb = rho_b * log2z + log2(per_elem_b)

        # ── C_coll: costo de verificar candidatos ─────────────────────────────
        # C_coll >= |L_a|*|L_b|*z^{-ell_t}*p^{-ell}*(ja+jb)*log2(p)
        verify_factor = (ja + jb) * log2p
        if verify_factor <= 0:
            return inf, inf
        log_Ccoll = (
            rho_a * log2z
            + rho_b * log2z
            - ell_t * log2z
            - ell   * log2p
            + log2(verify_factor)
        )

        # ── C_iter = C_Gauss + C_a + C_b + C_coll ────────────────────────────
        T_gauss = self._gaussian_elimination_complexity()
        log_C_iter = _log_sum_exp(T_gauss, log_Ca, log_Cb, log_Ccoll)
        if log_C_iter <= 0:
            return inf, inf

        # ── Término A: iteración interna ──────────────────────────────────────
        # A = (C_iter / N_sol) * log2(M)
        # log2(A) = log_C_iter - log_N_sol + log2(memory)   [memory = log2(M)]
        log_N_sol = self.problem.expected_number_solutions()
        if memory <= 1:
            return inf, inf
        log_A = log_C_iter - log_N_sol + log2(memory)

        # ── Término B: búsqueda de subcódigo ──────────────────────────────────
        # B = 1/(P_a * P_b)  →  log2(B) = -(log_Pa + log_Pb)
        log_Pa = _log2_P(ja, da, n, m, z)
        log_Pb = _log2_P(jb, db, n, m, z)
        log_B  = -(log_Pa + log_Pb)   # >= 0 dado que log_Pa, log_Pb <= 0

        # ── Total = A + B (log-sum-exp) ───────────────────────────────────────
        if log_A <= 0 and log_B <= 0:
            return inf, memory

        time = _log_sum_exp(log_A, log_B)
        if time <= 0 or time == inf:
            return inf, memory

        if verbose_information is not None:
            verbose_information.update({
                "rho_a": rho_a, "rho_b": rho_b,
                "ell":   ell,   "ell_t": ell_t,
                "log_Ca": log_Ca, "log_Cb": log_Cb, "log_Ccoll": log_Ccoll,
                "log_C_iter": log_C_iter,
                "log_Pa": log_Pa, "log_Pb": log_Pb,
                "log_A": log_A,   "log_B": log_B,
            })

        return time, memory

    def __repr__(self):
        return f"CollisionSearch (Submatrix Stern/Dumer) for R-SDP(G) with {self.problem}"
