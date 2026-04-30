"""
Constantes para el estimador CROSS
"""

# Parámetros de CROSS por nivel de seguridad (NIST)
CROSS_PARAMETERS = {
    # CROSS-R-SDP (RSDP)
    'CROSS-R-SDP-128': {
        'n': 126,      # N
        'k': 63,       # K
        'w': 35,       # peso del error (número de elementos no cero)
        't': 17,       # peso de restricción (z)
        'm': None,     # no usado en RSDP
        'lambda': 128,
        'variant': 'RSDP'
    },
    'CROSS-R-SDP-192': {
        'n': 190,
        'k': 95,
        'w': 53,
        't': 26,
        'm': None,
        'lambda': 192,
        'variant': 'RSDP'
    },
    'CROSS-R-SDP-256': {
        'n': 254,
        'k': 127,
        'w': 71,
        't': 35,
        'm': None,
        'lambda': 256,
        'variant': 'RSDP'
    },
    # CROSS-R-SDPG (RSDP con Gaussian elimination)
    'CROSS-R-SDPG-128': {
        'n': 112,      # N
        'k': 56,       # K
        'w': 28,       # peso del error  
        't': 14,       # peso de restricción
        'm': 12,       # M (parámetro adicional para RSDPG)
        'lambda': 128,
        'variant': 'RSDPG'
    },
    'CROSS-R-SDPG-192': {
        'n': 168,
        'k': 84,
        'w': 42,
        't': 21,
        'm': 18,
        'lambda': 192,
        'variant': 'RSDPG'
    },
    'CROSS-R-SDPG-256': {
        'n': 224,
        'k': 112,
        'w': 56,
        't': 28,
        'm': 24,
        'lambda': 256,
        'variant': 'RSDPG'
    }
}

# Constantes del algoritmo de firma
HASH_DIGEST_LENGTH = 32  # SHA-256 o similar
SALT_LENGTH = 16
SEED_LENGTH = 32

# Número de iteraciones del protocolo ZK
ZK_ROUNDS = 't'  # La T de CROSS es el número de rondas

# Algoritmos de ataque disponibles
ATTACK_ALGORITHMS = [
    'Stern',
    'Lee_Brickell', 
    'Leon',
    'BJMM',
    'May_Ozerov',
    'Both_May',
    'ISD_generic'
]