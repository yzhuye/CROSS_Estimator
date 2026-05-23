"""
Generador de instancias R-SDP para experimentos de caracterización de d_reg.

Cada instancia consiste en:
  - Matriz de paridad H ∈ F_p^{(n-k) × n}   (uniforme aleatoria)
  - Vector de error  e ∈ E^n                (peso w)
  - Síndrome         s = e · H^T ∈ F_p^{n-k}
  - Metadata: parámetros, semilla, generador g del subgrupo E

Las instancias se serializan en JSON para ser consumidas por el driver
SageMath/MAGMA que ejecuta F4/F5 sobre el sistema polinomial asociado.

Uso:
    python generate_instances.py
"""

import json
from pathlib import Path

import numpy as np

from config import (
    PARAMETER_GRID,
    SEEDS_PER_CONFIG,
    INSTANCES_DIR,
)


# ─────────────────────────────────────────────────
# Construcción del subgrupo E ⊂ F_p*
# ─────────────────────────────────────────────────

def find_generator_of_prime_order(p: int, z: int) -> int:
    """
    Encuentra g ∈ F_p* de orden primo z.

    Estrategia: g = a^((p-1)/z) para a aleatorio.
    Como z es primo, si g != 1 entonces ord(g) = z.

    Args:
        p (int): Primo (campo F_p).
        z (int): Orden primo. Debe dividir a p-1.

    Returns:
        int: Generador g.
    """
    if (p - 1) % z != 0:
        raise ValueError(f"z = {z} no divide a p - 1 = {p - 1}")
    exponent = (p - 1) // z
    for a in range(2, p):
        g = pow(a, exponent, p)
        if g != 1:
            return g
    raise ValueError(f"No se encontró generador de orden {z} en F_{p}")


def build_subgroup_E(p: int, z: int) -> list[int]:
    """
    Construye el subgrupo cíclico E = {g, g^2, ..., g^z} ⊂ F_p*.

    Returns:
        list[int]: Los z elementos de E.
    """
    g = find_generator_of_prime_order(p, z)
    return [pow(g, i, p) for i in range(1, z + 1)]


# ─────────────────────────────────────────────────
# Generación de instancia
# ─────────────────────────────────────────────────

def generate_instance(n: int, k: int, w: int, p: int, z: int, seed: int) -> dict:
    """
    Genera una instancia única de R-SDP.

    Args:
        n, k, w, p, z (int): Parámetros del problema.
        seed (int): Semilla para reproducibilidad.

    Returns:
        dict con la instancia completa serializable a JSON.
    """
    rng = np.random.default_rng(seed)

    # Subgrupo E
    g = find_generator_of_prime_order(p, z)
    E = [pow(g, i, p) for i in range(1, z + 1)]

    # Matriz H ∈ F_p^{(n-k) × n} uniforme
    H = rng.integers(0, p, size=(n - k, n), dtype=np.int64)

    # Vector e ∈ E^n con peso w
    e = np.zeros(n, dtype=np.int64)
    if w == n:
        support = np.arange(n)
    else:
        support = rng.choice(n, size=w, replace=False)
    for i in support:
        e[i] = E[rng.integers(0, z)]

    # Síndrome s = e · H^T mod p
    s = (H @ e) % p

    # Verificación de consistencia
    assert np.all((H @ e) % p == s), "Síndrome inconsistente"

    return {
        "n": int(n), "k": int(k), "w": int(w),
        "p": int(p), "z": int(z),
        "seed": int(seed),
        "g": int(g),
        "E": [int(x) for x in E],
        "H": H.tolist(),
        "e": e.tolist(),
        "s": s.tolist(),
    }


# ─────────────────────────────────────────────────
# Pipeline principal
# ─────────────────────────────────────────────────

def instance_filename(params: dict, seed: int) -> str:
    return (
        f"n{params['n']}_k{params['k']}_w{params['w']}"
        f"_z{params['z']}_p{params['p']}_s{seed}.json"
    )


def main() -> None:
    INSTANCES_DIR.mkdir(parents=True, exist_ok=True)

    n_generated = 0
    n_skipped = 0
    for params in PARAMETER_GRID:
        for seed in range(SEEDS_PER_CONFIG):
            try:
                instance = generate_instance(**params, seed=seed)
            except (ValueError, AssertionError) as e:
                print(f"  ⚠️  Skip {params} seed={seed}: {e}")
                n_skipped += 1
                continue

            path = INSTANCES_DIR / instance_filename(params, seed)
            with open(path, "w") as f:
                json.dump(instance, f, indent=2)
            n_generated += 1

    print(f"✅ Generadas {n_generated} instancias en {INSTANCES_DIR}")
    if n_skipped:
        print(f"⚠️  Saltadas {n_skipped} instancias")


if __name__ == "__main__":
    main()