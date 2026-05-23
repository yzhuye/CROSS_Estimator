import pytest
from math import inf
from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDPG import (
    CollisionSearch, Stern_G,
)
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDP import Stern

NIST1_G = dict(n=55,  k=36, m=25, z=127, p=509)
NIST3_G = dict(n=79,  k=48, m=40, z=127, p=509)
NIST5_G = dict(n=106, k=64, m=55, z=127, p=509)


# ── Validación principal (Example 16) ─────────────────────────────────────────

def test_nist1_time_target():
    """Target [2^143.1, 2^144.5] del Example 16 de la spec."""
    from app.estimator.cross_estimator import estimate_collision_search
    result = estimate_collision_search(**NIST1_G)
    t = result["optimal"]["time"]
    assert t is not None, "No se encontró solución"
    assert 143.1 <= t <= 144.5, f"Tiempo {t:.2f} fuera de [143.1, 144.5]"


def test_nist1_memory_target():
    """Memoria NIST-1 en [2^130, 2^136]."""
    from app.estimator.cross_estimator import estimate_collision_search
    result = estimate_collision_search(**NIST1_G)
    mem = result["optimal"]["memory"]
    assert mem is not None
    assert 130 <= mem <= 136, f"Memoria {mem:.2f} fuera de [130, 136]"


def test_nist1_optimal_params():
    """Parámetros óptimos: ja=19, da=1, jb=23, db=4 (Example 16 §8.2)."""
    from app.estimator.cross_estimator import estimate_collision_search
    result = estimate_collision_search(**NIST1_G)
    opt = result["optimal"]
    assert opt["ja"] == 19, f"ja={opt['ja']} esperado 19"
    assert opt["da"] == 1,  f"da={opt['da']} esperado 1"
    assert opt["jb"] == 23, f"jb={opt['jb']} esperado 23"
    assert opt["db"] == 4,  f"db={opt['db']} esperado 4"


# ── Punto exacto del Example 16 ───────────────────────────────────────────────

def test_example16_exact_point():
    """Evaluación directa del punto óptimo del Example 16."""
    p = CROSSProblem(n=55, k=36, z=127, p=509, m=25)
    cs = CollisionSearch(p, bit_complexities=1)
    params = {"ja": 19, "jb": 23, "da": 1, "db": 4}
    t, mem = cs._time_and_memory_complexity(params)
    assert 143.1 <= t   <= 144.5, f"time={t:.2f}"
    assert 130   <= mem <= 136,   f"memory={mem:.2f}"


# ── Validación P(j,d) — Ejemplo 14 SecurityDetails ───────────────────────────

def test_log2_P_values():
    """P(19,1) ≈ 0.45 (log2 ≈ -1.1) y P(23,4) ≈ 2^{-114} a 2^{-120}."""
    from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms.RSDPG.collision_search import _log2_P
    p19 = _log2_P(19, 1, 55, 25, 127)
    p23 = _log2_P(23, 4, 55, 25, 127)
    assert -5.0 <= p19 <= 0.0,   f"P(19,1) log2={p19:.2f} esperado cerca de 0"
    assert -130 <= p23 <= -100,  f"P(23,4) log2={p23:.1f} esperado ~-114"


# ── Prerequisito: requiere R-SDP(G) ──────────────────────────────────────────

def test_raises_without_rsdpg():
    """CollisionSearch debe lanzar ValueError para R-SDP puro (sin m)."""
    p = CROSSProblem(n=127, k=76)
    with pytest.raises(ValueError, match="R-SDP\\(G\\)"):
        CollisionSearch(p)


# ── Parámetros inválidos rechazados ──────────────────────────────────────────

def test_invalid_params_rejected():
    """_are_parameters_invalid rechaza casos degenerados."""
    p = CROSSProblem(**NIST1_G)
    cs = CollisionSearch(p, bit_complexities=1)

    n, k = 55, 36
    assert cs._are_parameters_invalid({"ja": 0,  "jb": 10, "da": 1, "db": 1})   # ja=0
    assert cs._are_parameters_invalid({"ja": 30, "jb": 30, "da": 1, "db": 1})   # ja+jb>n
    assert cs._are_parameters_invalid({"ja": 5,  "jb": 5,  "da": 1, "db": 1})   # ell<=0
    assert cs._are_parameters_invalid({"ja": 10, "jb": 10, "da": 10, "db": 1})  # da>=ja


# ── Comparativo: CollisionSearch < Stern_G ────────────────────────────────────

def test_collision_search_better_than_stern_g():
    """CollisionSearch debe dar tiempo MENOR que Stern_G para NIST-1."""
    from app.estimator.cross_estimator import estimate_collision_search, estimate_stern_g
    cs_result = estimate_collision_search(**NIST1_G)
    sg_result  = estimate_stern_g(**NIST1_G)
    cs_time = cs_result["optimal"]["time"]
    sg_time  = sg_result["optimal"]["time"]
    assert cs_time is not None and sg_time is not None
    assert cs_time < sg_time, (
        f"CollisionSearch ({cs_time:.1f}) >= Stern_G ({sg_time:.1f})"
    )


# ── Stern R-SDP produce resultados razonables ─────────────────────────────────

def test_stern_rsdp_reasonable():
    """Stern sobre R-SDP estándar (sin m) produce tiempo y memoria finitos."""
    p = CROSSProblem(n=127, k=76)
    s = Stern(p, bit_complexities=1)
    best_time = inf
    for params in s._valid_choices():
        t, mem = s._time_and_memory_complexity(params)
        if t < best_time:
            best_time = t
    assert best_time != inf and best_time > 0, "Stern no encontró solución"
    assert 100 <= best_time <= 250, f"Stern time={best_time:.2f} fuera de rango razonable"
