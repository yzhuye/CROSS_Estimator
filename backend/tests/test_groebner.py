"""
Tests mínimos para el módulo Gröbner del estimador CROSS.

Estos tests validan:
  - Instanciación correcta.
  - Salida finita y positiva.
  - Monotonía respecto a omega.
  - Monotonía respecto al tamaño del problema.

NOTA: Validación cuantitativa contra valores experimentales pendiente hasta
que el modelo de d_reg esté calibrado (ver experiments/groebner/).
"""

import pytest
from cryptographic_estimators.CROSSEstimator import CROSSProblem
from cryptographic_estimators.CROSSEstimator.CROSSAlgorithms import Groebner


# Parámetros CROSS-R-SDP por nivel NIST (CROSS spec v1.2)
CROSS_PARAMS = {
    "cat1": {"n": 127, "k": 76,  "p": 127, "z": 7},
    "cat3": {"n": 187, "k": 111, "p": 127, "z": 7},
    "cat5": {"n": 251, "k": 150, "p": 127, "z": 7},
}


@pytest.fixture(params=list(CROSS_PARAMS.keys()))
def nist_problem(request):
    params = CROSS_PARAMS[request.param]
    return CROSSProblem(
        n=params["n"], k=params["k"],
        p=params["p"], z=params["z"]
    )


def test_instantiation():
    """Instanciación con parámetros válidos sin errores."""
    problem = CROSSProblem(n=127, k=76)
    g = Groebner(problem, bit_complexities=1)
    assert g is not None
    assert g._name == "Groebner"


def test_time_complexity_is_finite(nist_problem):
    """time_complexity() retorna un valor finito para todos los niveles NIST."""
    g = Groebner(nist_problem, bit_complexities=1)
    t = g.time_complexity()
    assert t < float("inf"), "time_complexity() retornó infinito"
    assert t > 0, "time_complexity() retornó un valor no positivo"


def test_memory_complexity_is_finite(nist_problem):
    """memory_complexity() retorna un valor finito para todos los niveles NIST."""
    g = Groebner(nist_problem, bit_complexities=1)
    m = g.memory_complexity()
    assert m < float("inf"), "memory_complexity() retornó infinito"
    assert m > 0, "memory_complexity() retornó un valor no positivo"


def test_time_geq_memory(nist_problem):
    """Con omega ≥ 2, el tiempo debe ser ≥ que la memoria (cota de coherencia)."""
    g = Groebner(nist_problem, omega=2.0, bit_complexities=1)
    assert g.time_complexity() >= g.memory_complexity()


def test_omega_monotonic():
    """Mayor omega ⇒ mayor complejidad temporal (relación monótona)."""
    problem = CROSSProblem(n=127, k=76)
    g_min = Groebner(problem, omega=2.00, bit_complexities=1)
    g_str = Groebner(problem, omega=2.81, bit_complexities=1)
    assert g_str.time_complexity() > g_min.time_complexity()


def test_complexity_grows_with_n():
    """Para k/n constante, mayor n ⇒ mayor complejidad."""
    g_cat1 = Groebner(CROSSProblem(n=127, k=76),  bit_complexities=1)
    g_cat3 = Groebner(CROSSProblem(n=187, k=111), bit_complexities=1)
    g_cat5 = Groebner(CROSSProblem(n=251, k=150), bit_complexities=1)
    assert g_cat3.time_complexity() > g_cat1.time_complexity()
    assert g_cat5.time_complexity() > g_cat3.time_complexity()


def test_verbose_information():
    """El dict verbose_information se llena correctamente."""
    problem = CROSSProblem(n=127, k=76)
    g = Groebner(problem, bit_complexities=1)
    verbose = {}
    g._time_and_memory_complexity({"r": 0}, verbose_information=verbose)
    assert "d_reg" in verbose
    assert "log2_N" in verbose
    assert "omega" in verbose
    assert verbose["d_reg"] > 0