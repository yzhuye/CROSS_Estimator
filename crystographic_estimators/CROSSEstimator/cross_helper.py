"""
Funciones auxiliares para el estimador CROSS
"""

from math import log2, comb, factorial

def estimate_forgery_complexity(problem):
    """
    Estima complejidad de ataques de falsificación
    
    En CROSS, la falsificación requiere:
    1. Adivinar el chall enge correcto
    2. O resolver el problema RSDP subyacente
    """
    n = problem.n
    w = problem.w
    t = problem.t
    
    # Probabilidad de adivinar el challenge correcto
    total_challenges = comb(n, w)
    prob_success = 1 / total_challenges
    
    # Complejidad esperada
    forgery_complexity = 1 / prob_success
    
    return {
        'complexity': forgery_complexity,
        'bits': log2(forgery_complexity),
        'type': 'challenge_guessing'
    }


def estimate_key_recovery(problem):
    """
    Estima complejidad de recuperación de clave secreta
    
    Requiere resolver el problema RSDP subyacente
    """
    # La recuperación de clave es equivalente a resolver RSDP
    return {
        'complexity': 'Same as RSDP problem',
        'bits': 'Same as RSDP problem'
    }


def optimize_CROSS_parameters(lambda_target=128, max_n=300):
    """
    Optimiza parámetros de CROSS para un nivel de seguridad dado
    
    Busca los menores n, k que alcancen lambda_target bits de seguridad
    """
    from .cross_estimator import CROSSEstimator
    
    best_params = None
    best_size = float('inf')
    
    for n in range(100, max_n + 1, 2):
        for k in range(n // 4, 3 * n // 4, 2):
            for w in range(20, min(80, n // 2)):
                t = w // 2  # Regla general para CROSS
                
                estimator = CROSSEstimator(n=n, k=k, w=w, t=t)
                security = estimator.estimate()
                
                if security['bit_security'] >= lambda_target:
                    size = n + (n - k)  # Tamaño total
                    if size < best_size:
                        best_size = size
                        best_params = {
                            'n': n, 'k': k, 'w': w, 't': t,
                            'bit_security': security['bit_security'],
                            'total_size': size
                        }
    
    return best_params


def format_complexity(complexity):
    """
    Formatea números de complejidad grandes de manera legible
    """
    if complexity == float('inf'):
        return '∞'
    elif complexity > 10**100:
        return f"2^{log2(complexity):.1f}"
    elif complexity > 10**6:
        return f"{complexity:.2e}"
    else:
        return f"{complexity:.0f}"