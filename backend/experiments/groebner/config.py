"""
Configuración del pipeline experimental para caracterización de d_reg.

Define la grilla de parámetros (n, k, w, z) a explorar y las rutas
de almacenamiento de instancias y resultados.
"""

from itertools import product
from pathlib import Path

# ─────────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────────
EXPERIMENT_DIR  = Path(__file__).parent.resolve()
DATA_DIR        = EXPERIMENT_DIR / "data"
INSTANCES_DIR   = DATA_DIR / "instances"
RESULTS_FILE    = DATA_DIR / "results.csv"
MODELS_DIR      = EXPERIMENT_DIR / "models"

# ─────────────────────────────────────────────────
# Parámetros del problema
# ─────────────────────────────────────────────────
P = 127                       # Característica del cuerpo finito (CROSS default)

# Empezamos con grilla CONSERVADORA para validar el pipeline.
# Expandir después según design_experimental.pdf.
N_VALUES   = [4, 6, 8, 10, 12]   # Tamaño del problema
K_RATIOS   = [0.3, 0.5, 0.7]           # k = round(n * ratio)
W_RATIOS   = [1.0]               # w = round(n * ratio); 1.0 = peso completo
Z_VALUES   = [3, 7]              # Orden del subgrupo (CROSS default)
SEEDS_PER_CONFIG = 5             # Repeticiones por (n, k, w, z)

# ─────────────────────────────────────────────────
# Construcción de la grilla
# ─────────────────────────────────────────────────
def build_parameter_grid() -> list[dict]:
    """
    Producto cartesiano de los rangos, descartando configuraciones inválidas:
      - k >= n
      - w > n o w < 1
      - z no divide a p-1
    """
    grid = []
    for n, kr, wr, z in product(N_VALUES, K_RATIOS, W_RATIOS, Z_VALUES):
        k = max(1, round(n * kr))
        w = round(n * wr)
        if k >= n or w > n or w < 1:
            continue
        if (P - 1) % z != 0:
            continue
        grid.append({"n": n, "k": k, "w": w, "p": P, "z": z})
    return grid


PARAMETER_GRID = build_parameter_grid()


if __name__ == "__main__":
    print(f"Total configuraciones: {len(PARAMETER_GRID)}")
    print(f"Total instancias previstas: {len(PARAMETER_GRID) * SEEDS_PER_CONFIG}")
    for cfg in PARAMETER_GRID[:5]:
        print(f"  {cfg}")