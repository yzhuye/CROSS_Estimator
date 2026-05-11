from enum import Enum


class VerboseInformation(Enum):
    """
    Constantes para información detallada (verbose) en los algoritmos CROSS.
    """
    GAUSS = "gauss"
    LISTS = "lists"
    CONSTRAINTS = "constraints"
    REPRESENTATIONS = "representation"


# Constantes del problema CROSS según el paper oficial
class CROSSDefaults:
    """Valores por defecto para los parámetros de CROSS."""
    P = 127          # Característica del cuerpo finito
    Z = 7            # Orden del subgrupo E
    Z_D = 35         # Tamaño del conjunto auxiliar D
    ALPHA_E = 1      # Aditividad de E
    ALPHA_D = 5      # Aditividad de D


# Categorías NIST y sus umbrales de seguridad según CROSS
NIST_CATEGORIES = {
    1: 143,   # AES-128 equivalente
    3: 207,   # AES-192 equivalente
    5: 272,   # AES-256 equivalente
}