"""
analyze_results.py — Ajuste del modelo d_reg(n, k, w, z).

Carga results.csv producido por run_f4.sage, ajusta las tres formas
funcionales propuestas en grobner_diseno_experimental.pdf §6.1, compara
con AIC/BIC/R², y exporta el modelo ganador a models/d_reg_model.json
para ser consumido por groebner.py (sustituye el stub d_reg = c·n).

Workflow:
  1. Carga results.csv y filtra filas válidas.
  2. Ajusta tres formas funcionales (lineal, logarítmica, mixta).
  3. Selecciona la mejor por BIC (criterio conservador).
  4. Exporta el modelo a JSON.
  5. Produce gráficos diagnósticos en plots/.

Uso:
    python analyze_results.py
"""

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


EXPERIMENT_DIR = Path(__file__).parent.resolve()
RESULTS_FILE   = EXPERIMENT_DIR / "data" / "results.csv"
MODELS_DIR     = EXPERIMENT_DIR / "models"
PLOTS_DIR      = EXPERIMENT_DIR / "plots"


def model_linear(X, a0, a1, a2, a3, a4):
    """d_reg = a0 + a1·n + a2·k + a3·w + a4·z"""
    n, k, w, z = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    return a0 + a1 * n + a2 * k + a3 * w + a4 * z


def model_logarithmic(X, a0, a1, a2, a3):
    """d_reg = a0 + a1·n + a2·log(z) + a3·(n-k)"""
    n, k, _, z = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    return a0 + a1 * n + a2 * np.log(z) + a3 * (n - k)


def model_mixed(X, a0, a1, a2, a3, a4):
    """d_reg = a0 + a1·n + a2·(n-k) + a3·(w/n) + a4·log(z)"""
    n, k, w, z = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    return a0 + a1 * n + a2 * (n - k) + a3 * (w / n) + a4 * np.log(z)


MODELS = {
    "linear":      {"func": model_linear,      "n_params": 5,
                    "feature_order": ["intercept", "n", "k", "w", "z"]},
    "logarithmic": {"func": model_logarithmic, "n_params": 4,
                    "feature_order": ["intercept", "n", "log_z", "n_minus_k"]},
    "mixed":       {"func": model_mixed,       "n_params": 5,
                    "feature_order": ["intercept", "n", "n_minus_k",
                                      "w_over_n", "log_z"]},
}


def compute_metrics(y, y_pred, k_params):
    n = len(y)
    rss = float(np.sum((y - y_pred) ** 2))
    if rss <= 0:
        return {"r_squared": 1.0, "aic": float("-inf"),
                "bic": float("-inf"), "rss": 0.0}
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - rss / ss_tot if ss_tot > 0 else float("nan")
    log_lik = -n / 2 * np.log(rss / n)
    aic = 2 * k_params - 2 * log_lik
    bic = k_params * np.log(n) - 2 * log_lik
    return {"r_squared": float(r2), "aic": float(aic),
            "bic": float(bic), "rss": rss}


def load_data() -> pd.DataFrame:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"No existe {RESULTS_FILE}")

    df = pd.read_csv(RESULTS_FILE)
    print(f"📊 Cargadas {len(df)} filas de {RESULTS_FILE.name}")

    valid = df[
        (df["status"] == "ok") &
        (df["solution_verified"] == True) &
        (df["d_reg_empirical"] > 0)
    ].copy()
    print(f"   Filas válidas para regresión: {len(valid)}")

    if len(valid) > 0:
        n_range = (valid["n"].min(), valid["n"].max())
        k_range = (valid["k"].min(), valid["k"].max())
        z_range = (valid["z"].min(), valid["z"].max())
        print(f"   Rangos: n∈[{n_range[0]},{n_range[1]}], "
              f"k∈[{k_range[0]},{k_range[1]}], "
              f"z∈[{z_range[0]},{z_range[1]}]")
    return valid


def make_plots(df, fits, best_name):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    for z_val in sorted(df["z"].unique()):
        sub = df[df["z"] == z_val]
        ax.scatter(sub["n"], sub["d_reg_empirical"],
                   label=f"z={z_val}", alpha=0.65, s=40)
    ax.set_xlabel("n"); ax.set_ylabel("d_reg empírico")
    ax.set_title("Grado de regularidad observado vs n")
    ax.legend(); ax.grid(alpha=0.3)
    fig.savefig(PLOTS_DIR / "d_reg_vs_n.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for z_val in sorted(df["z"].unique()):
        sub = df[df["z"] == z_val]
        agg = sub.groupby("n")["time_sec"].mean()
        ax.semilogy(agg.index, agg.values, "o-", label=f"z={z_val}")
    ax.set_xlabel("n"); ax.set_ylabel("tiempo (s) [log]")
    ax.set_title("Tiempo de cómputo F4 vs n")
    ax.legend(); ax.grid(alpha=0.3, which="both")
    fig.savefig(PLOTS_DIR / "time_vs_n.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, len(fits), figsize=(5 * len(fits), 5),
                             squeeze=False)
    for ax, (name, fit) in zip(axes[0], fits.items()):
        y_actual = fit["y_actual"]
        y_pred = fit["y_pred"]
        ax.scatter(y_actual, y_pred, alpha=0.6, s=40,
                   color=("crimson" if name == best_name else "steelblue"))
        lo = min(y_actual.min(), y_pred.min())
        hi = max(y_actual.max(), y_pred.max())
        ax.plot([lo, hi], [lo, hi], "k--", alpha=0.5, label="y = x")
        title = f"{name}\nR²={fit['metrics']['r_squared']:.3f}"
        if name == best_name:
            title += "  ★ ganador"
        ax.set_xlabel("d_reg observado"); ax.set_ylabel("d_reg predicho")
        ax.set_title(title); ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "predictions_vs_actual.png",
                dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"📈 Gráficos guardados en {PLOTS_DIR}/")


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    if len(df) < 10:
        print(f"⚠️  Pocas filas válidas ({len(df)}). La regresión no será robusta.")
        if len(df) < 4:
            print("❌ Insuficientes datos para ajustar. Aborta.")
            return

    X = df[["n", "k", "w", "z"]].values.astype(float)
    y = df["d_reg_empirical"].values.astype(float)

    print("\n📐 Ajustando formas funcionales...\n")
    print(f"{'modelo':<15s} {'k':>3s} {'R²':>8s} {'AIC':>10s} {'BIC':>10s}")
    print("-" * 50)

    fits = {}
    for name, info in MODELS.items():
        try:
            popt, _ = curve_fit(info["func"], X, y,
                                p0=[1.0] * info["n_params"], maxfev=10000)
            y_pred = info["func"](X, *popt)
            metrics = compute_metrics(y, y_pred, info["n_params"])
            fits[name] = {"coefficients": popt.tolist(), "metrics": metrics,
                          "y_pred": y_pred, "y_actual": y}
            print(f"{name:<15s} {info['n_params']:>3d} "
                  f"{metrics['r_squared']:>8.4f} "
                  f"{metrics['aic']:>10.2f} {metrics['bic']:>10.2f}")
        except Exception as ex:
            print(f"{name:<15s} FAIL: {ex}")

    if not fits:
        print("❌ Ningún modelo se pudo ajustar.")
        return

    best_name, best_fit = min(fits.items(),
                              key=lambda kv: kv[1]["metrics"]["bic"])
    print(f"\n🏆 Mejor modelo (por BIC): {best_name}")
    print(f"   Coeficientes: {best_fit['coefficients']}")
    print(f"   R² = {best_fit['metrics']['r_squared']:.4f}")

    output = {
        "best_model": best_name,
        "coefficients": best_fit["coefficients"],
        "feature_order": MODELS[best_name]["feature_order"],
        "metrics": best_fit["metrics"],
        "all_models": {
            name: {"coefficients": fit["coefficients"],
                   "metrics": fit["metrics"],
                   "feature_order": MODELS[name]["feature_order"]}
            for name, fit in fits.items()
        },
        "n_instances_used": int(len(df)),
        "parameter_ranges": {
            "n": [int(df["n"].min()), int(df["n"].max())],
            "k": [int(df["k"].min()), int(df["k"].max())],
            "z": [int(df["z"].min()), int(df["z"].max())],
        },
        "fitted_at": datetime.now().isoformat(timespec="seconds"),
    }
    out_path = MODELS_DIR / "d_reg_model.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n💾 Modelo guardado en {out_path}")

    make_plots(df, fits, best_name)


if __name__ == "__main__":
    main()
