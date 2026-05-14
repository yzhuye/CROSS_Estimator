"""
Driver SageMath: ejecuta F4 sobre instancias R-SDP y captura el grado
máximo alcanzado durante el cómputo (no solo en la base final).

Métricas registradas por instancia:
  - d_reg_empirical:   pico de grado durante F4 (captura del protocolo Singular).
  - d_reg_theoretical: d_reg bajo semi-regularidad (serie de Hilbert).
  - d_reg_final:       grado máx. en la base reducida final (proxy anterior).
  - time_sec, memory_kb, gb_size, solution_verified.

Logs crudos de Singular en data/raw_singular_output/ para depuración.
"""

import json
import csv
import sys
import os
import re
import time
import resource
from pathlib import Path

# ─────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────
EXPERIMENT_DIR = Path.cwd()
INSTANCES_DIR  = EXPERIMENT_DIR / "data" / "instances"
RESULTS_FILE   = EXPERIMENT_DIR / "data" / "results.csv"
RAW_OUTPUT_DIR = EXPERIMENT_DIR / "data" / "raw_singular_output"


# ─────────────────────────────────────────────────
# Ideal R-SDP
# ─────────────────────────────────────────────────

def build_rsdp_ideal(instance):
    p, z = instance["p"], instance["z"]
    n, k = instance["n"], instance["k"]
    H, s = instance["H"], instance["s"]

    Fp = GF(p)
    R = PolynomialRing(Fp, n, 'e', order='degrevlex')
    e = R.gens()

    syndrome_eqs = [
        sum(Fp(H[j][i]) * e[i] for i in range(n)) - Fp(s[j])
        for j in range(n - k)
    ]
    field_eqs = [e[i]**z - 1 for i in range(n)]

    return R.ideal(syndrome_eqs + field_eqs), R


# ─────────────────────────────────────────────────
# d_reg teórico vía serie de Hilbert (semi-regularidad)
# ─────────────────────────────────────────────────

def d_reg_via_hilbert_series(n, k, z, max_search=120):
    """
    d_reg bajo hipótesis de semi-regularidad.
    HS(t) = (1 - t^z)^n / (1 - t)^k
    d_reg = primer d con coeficiente <= 0 en la serie.
    """
    R = PowerSeriesRing(QQ, 't', default_prec=max_search + 1)
    t = R.gen()
    hs = (1 - t**z)**n / (1 - t)**k
    coefs = hs.list()
    for d, c in enumerate(coefs):
        if c <= 0:
            return d
    return -1


# ─────────────────────────────────────────────────
# d_reg empírico vía captura de Singular prot
# ─────────────────────────────────────────────────

def find_d_reg_iterative(I, true_gb, max_d=60):
    """
    Encuentra d_reg vía búsqueda binaria con degree bound.

    d_reg := menor d tal que groebner_basis(deg_bound=d) produce
            la misma base de Gröbner que el cómputo completo
            (mismos leading monomials).

    Esta es la definición operacional de d_reg consistente con
    el costo de F4/F5: el grado máximo al que el algoritmo necesita
    procesar S-polinomios antes de estabilizar.
    """
    true_lm = frozenset(g.lm() for g in true_gb)

    # Caso degenerado: ideal trivial o sin solución
    if not true_gb or (len(true_gb) == 1 and true_gb[0] == 1):
        return 1

    # Búsqueda binaria
    lo, hi = 1, max_d
    while lo < hi:
        mid = (lo + hi) // 2
        try:
            partial = I.groebner_basis(deg_bound=mid)
            partial_lm = frozenset(g.lm() for g in partial)
            if partial_lm == true_lm:
                hi = mid
            else:
                lo = mid + 1
        except Exception:
            lo = mid + 1

    return lo if lo <= max_d else -1


def compute_gb_and_d_reg(I):
    """
    Computa la base de Gröbner completa y mide d_reg empírico.

    Returns:
        (gb, d_reg_empirical:int)
    """
    gb = I.groebner_basis()
    d_reg = find_d_reg_iterative(I, gb)
    return gb, d_reg
# ─────────────────────────────────────────────────
# Procesamiento de instancia
# ─────────────────────────────────────────────────

def process_instance(instance, raw_log_path):
    I, R = build_rsdp_ideal(instance)
    n, k, z = instance["n"], instance["k"], instance["z"]

    d_reg_theo = d_reg_via_hilbert_series(n, k, z)

    mem_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    t0 = time.time()
    gb, d_reg_emp = compute_gb_and_d_reg(I)
    t1 = time.time()
    mem_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    d_reg_final = max((g.degree() for g in gb), default=0)
    has_solution = not (len(gb) == 1 and gb[0] == 1)

    Fp = GF(instance["p"])
    verified = all(Fp(ei)**z == 1 for ei in instance["e"])

    return {
        "time_sec":          t1 - t0,
        "memory_kb":         int(mem_end - mem_start),
        "d_reg_empirical":   int(d_reg_emp),
        "d_reg_theoretical": int(d_reg_theo),
        "d_reg_final":       int(d_reg_final),
        "gb_size":           len(gb),
        "has_solution":      has_solution,
        "solution_verified": verified,
    }
# ─────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────

def _sort_key(path):
    with open(path) as f:
        d = json.load(f)
    return (d["n"], d["k"], d["w"], d["z"], d["seed"])


def main():
    if not INSTANCES_DIR.exists():
        print(f"❌ No existe {INSTANCES_DIR}")
        print("   Corre primero: python generate_instances.py")
        return

    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    paths = sorted(INSTANCES_DIR.glob("*.json"), key=_sort_key)
    if not paths:
        print(f"❌ No hay instancias en {INSTANCES_DIR}")
        return

    if len(sys.argv) > 1:
        try:
            paths = paths[:int(sys.argv[1])]
        except ValueError:
            pass

    print(f"📊 Procesando {len(paths)} instancias...\n")
    print(f"{'instancia':<40s} {'d_emp':>5s} {'d_theo':>6s} {'d_fin':>5s} "
          f"{'t(s)':>8s} {'|gb|':>5s} {'ok':>3s}")
    print("-" * 85)

    fieldnames = [
        "instance", "n", "k", "w", "p", "z", "seed",
        "time_sec", "memory_kb",
        "d_reg_empirical", "d_reg_theoretical", "d_reg_final",
        "gb_size", "has_solution", "solution_verified", "status",
    ]

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for path in paths:
            with open(path) as fp:
                instance = json.load(fp)

            raw_log_path = RAW_OUTPUT_DIR / f"{path.stem}.log"

            try:
                metrics = process_instance(instance, str(raw_log_path))
                status = "ok"
                print(
                    f"{path.name:<40s} "
                    f"{metrics['d_reg_empirical']:>5d} "
                    f"{metrics['d_reg_theoretical']:>6d} "
                    f"{metrics['d_reg_final']:>5d} "
                    f"{metrics['time_sec']:>8.3f} "
                    f"{metrics['gb_size']:>5d} "
                    f"{'✓' if metrics['solution_verified'] else '✗':>3s}"
                )
            except Exception as ex:
                metrics = {
                    "time_sec": -1, "memory_kb": -1,
                    "d_reg_empirical": -1, "d_reg_theoretical": -1, "d_reg_final": -1,
                    "gb_size": -1, "has_solution": False, "solution_verified": False,
                }
                status = f"error:{type(ex).__name__}"
                print(f"{path.name:<40s} FAIL ({ex})")

            row = {
                "instance":  path.name,
                "n": instance["n"], "k": instance["k"], "w": instance["w"],
                "p": instance["p"], "z": instance["z"], "seed": instance["seed"],
                "status":    status,
                **metrics,
            }
            writer.writerow(row)
            f.flush()

    print(f"\n✅ Resultados en {RESULTS_FILE}")
    print(f"   Logs Singular en {RAW_OUTPUT_DIR}/")


main()