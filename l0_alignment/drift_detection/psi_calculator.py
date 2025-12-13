from __future__ import annotations
import numpy as np

def _safe_hist(x: np.ndarray, bins: int = 10) -> tuple[np.ndarray, np.ndarray]:
    counts, edges = np.histogram(x, bins=bins)
    counts = counts.astype(np.float64)
    counts = counts / max(counts.sum(), 1.0)
    return counts, edges

def population_stability_index(expected: np.ndarray, actual: np.ndarray, bins: int = 10, eps: float = 1e-6) -> float:
    expected = np.asarray(expected).ravel()
    actual = np.asarray(actual).ravel()
    exp_counts, edges = _safe_hist(expected, bins=bins)
    act_counts, _ = np.histogram(actual, bins=edges)
    act_counts = act_counts.astype(np.float64)
    act_counts = act_counts / max(act_counts.sum(), 1.0)

    exp_counts = np.clip(exp_counts, eps, 1.0)
    act_counts = np.clip(act_counts, eps, 1.0)
    return float(np.sum((act_counts - exp_counts) * np.log(act_counts / exp_counts)))

def kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-8) -> float:
    p = np.asarray(p).ravel()
    q = np.asarray(q).ravel()
    p = p / max(p.sum(), eps)
    q = q / max(q.sum(), eps)
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    return float(np.sum(p * np.log(p / q)))
