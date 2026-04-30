"""
CROSS Estimator Package

Estimador de seguridad para el esquema de firma digital CROSS
basado en los problemas RSDP y RSDPG
"""

from .cross_problem import CROSSProblem
from .cross_algorithm import (
    SternAlgorithm,
    BJMMAlgorithm,
)
from .cross_estimator import CROSSEstimator
from .cross_constants import *
from .cross_helper import (
    estimate_forgery_complexity,
    estimate_key_recovery,
    optimize_CROSS_parameters
)

__all__ = [
    'CROSSProblem',
    'CROSSEstimator',
    'SternAlgorithm',
    'BJMMAlgorithm',
    'MayOzerovAlgorithm',
    'ISDGenericAlgorithm',
    'CROSS_PARAMETERS',
    'estimate_forgery_complexity',
    'estimate_key_recovery',
    'optimize_CROSS_parameters'
]

# Funciones de alto nivel para uso externo

def estimate_CROSS(params_or_name, algorithm='best'):
    """
    Función principal de estimación
    
    Uso:
    >>> results = estimate_CROSS('CROSS-R-SDP-128')
    >>> print(f"Bit security: {results['bit_security']}")
    
    >>> results = estimate_CROSS({'n': 126, 'k': 63, 'w': 35, 't': 17})
    """
    if isinstance(params_or_name, str):
        if params_or_name in CROSS_PARAMETERS:
            params = CROSS_PARAMETERS[params_or_name]
        else:
            raise ValueError(f"Unknown parameter set: {params_or_name}")
    else:
        params = params_or_name
    
    estimator = CROSSEstimator(**params)
    return estimator.estimate(algorithm=algorithm)


def compare_CROSS_variants():
    """
    Compara seguridad de todas las variantes de CROSS
    """
    results = {}
    for name, params in CROSS_PARAMETERS.items():
        estimator = CROSSEstimator(**params)
        results[name] = estimator.estimate()
        print(f"{name}: {results[name]['bit_security']:.1f} bits")
    return results