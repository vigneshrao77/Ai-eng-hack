import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger("modernrx.roadmap.montecarlo")


def sample_pert(
    opt: float, likely: float, pess: float, size: int, rng: np.random.Generator
) -> np.ndarray:
    """
    Samples from a PERT-Beta distribution.
    alpha = 1 + 4 * (likely - opt) / (pess - opt)
    beta = 1 + 4 * (pess - likely) / (pess - opt)
    """
    if pess <= opt:
        return np.full(size, likely)

    span = pess - opt
    alpha = 1.0 + 4.0 * (likely - opt) / span
    beta_param = 1.0 + 4.0 * (pess - likely) / span

    # Ensure shape parameters are strictly positive
    alpha = max(0.1, alpha)
    beta_param = max(0.1, beta_param)

    samples = opt + rng.beta(alpha, beta_param, size=size) * span
    return samples


def run_monte_carlo_simulation(
    scheduled_tasks: List[Dict[str, Any]],
    runs: int = 10000,
    target_weeks: Optional[float] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Runs 10,000 PERT Monte Carlo simulations across the modernization schedule DAG.
    Calculates P50, P80, P95 completion durations, probability of meeting target,
    and sensitivity ranking (tornado chart variance drivers).
    """
    if not scheduled_tasks:
        return {
            "p50_weeks": 0.0,
            "p80_weeks": 0.0,
            "p95_weeks": 0.0,
            "prob_meeting_target": 100.0,
            "histogram": [],
            "drivers_of_uncertainty": [],
        }

    rng = np.random.default_rng(seed)
    n_tasks = len(scheduled_tasks)
    task_ids = [t["id"] for t in scheduled_tasks]
    id_to_idx = {tid: i for i, tid in enumerate(task_ids)}

    # Sample duration matrix: shape (n_tasks, runs)
    duration_samples = np.zeros((n_tasks, runs), dtype=np.float64)

    for i, t in enumerate(scheduled_tasks):
        opt, likely, pess = t.get("effort_triple", (t["duration"] * 0.75, t["duration"], t["duration"] * 1.45))
        duration_samples[i, :] = sample_pert(opt, likely, pess, size=runs, rng=rng)

    # Topological order for propagating durations through DAG
    finish_times = np.zeros((n_tasks, runs), dtype=np.float64)
    start_times = np.zeros((n_tasks, runs), dtype=np.float64)

    # Sort tasks in topological order based on scheduled start_week
    sorted_indices = sorted(range(n_tasks), key=lambda i: scheduled_tasks[i]["start_week"])

    for idx in sorted_indices:
        t = scheduled_tasks[idx]
        deps = t.get("dependencies", [])
        if not deps:
            start_times[idx, :] = 0.0
        else:
            pred_indices = [id_to_idx[d] for d in deps if d in id_to_idx]
            if pred_indices:
                start_times[idx, :] = np.max(finish_times[pred_indices, :], axis=0)
            else:
                start_times[idx, :] = 0.0

        finish_times[idx, :] = start_times[idx, :] + duration_samples[idx, :]

    # Project makespan for each run
    project_makespans = np.max(finish_times, axis=0)

    # Percentiles
    p50 = float(np.percentile(project_makespans, 50))
    p80 = float(np.percentile(project_makespans, 80))
    p95 = float(np.percentile(project_makespans, 95))

    p50 = round(p50, 1)
    p80 = round(p80, 1)
    p95 = round(p95, 1)

    # Target probability
    if target_weeks is None:
        target_weeks = p80

    prob_meeting = float(np.mean(project_makespans <= target_weeks) * 100.0)
    prob_meeting = round(prob_meeting, 1)

    # Histogram (20 bins)
    hist_counts, bin_edges = np.histogram(project_makespans, bins=20)
    histogram = []
    for count, b_start, b_end in zip(hist_counts, bin_edges[:-1], bin_edges[1:]):
        histogram.append({
            "bin_start": round(float(b_start), 1),
            "bin_end": round(float(b_end), 1),
            "count": int(count),
        })

    # Sensitivity analysis: Pearson correlation with total makespan (Tornado Drivers)
    drivers = []
    for i, t in enumerate(scheduled_tasks):
        std_task = np.std(duration_samples[i, :])
        if std_task > 1e-4:
            corr = float(np.corrcoef(duration_samples[i, :], project_makespans)[0, 1])
        else:
            corr = 0.0
        drivers.append({
            "task_id": t["id"],
            "task_name": t.get("name", t["id"]),
            "gxp_tier": t.get("gxp_tier", "LOW"),
            "variance_contribution": round(max(0.0, corr) * 100.0, 1),
            "correlation": round(corr, 3),
        })

    drivers.sort(key=lambda d: d["variance_contribution"], reverse=True)

    return {
        "runs": runs,
        "p50_weeks": p50,
        "p80_weeks": p80,
        "p95_weeks": p95,
        "target_weeks": target_weeks,
        "prob_meeting_target": prob_meeting,
        "mean_weeks": round(float(np.mean(project_makespans)), 1),
        "std_weeks": round(float(np.std(project_makespans)), 1),
        "min_weeks": round(float(np.min(project_makespans)), 1),
        "max_weeks": round(float(np.max(project_makespans)), 1),
        "histogram": histogram,
        "drivers_of_uncertainty": drivers[:6],
    }
