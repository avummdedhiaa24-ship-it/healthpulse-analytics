"""
drift_service.py
────────────────
Computes data drift between a baseline distribution and a current
distribution for numeric features in the Patient table.
 
Two industry-standard statistics are calculated per feature:
 
  PSI  (Population Stability Index)
       < 0.10  → no drift
       0.10–0.20 → moderate drift (monitor)
       > 0.20  → significant drift (retrain)
 
  KS   (Kolmogorov-Smirnov statistic)
       Measures the maximum distance between two CDFs.
       > 0.10 → statistically significant distribution shift
 
Both must exceed their threshold for drift_detected = True.
Results are persisted to the drift_logs table automatically.
"""

import logging
from typing import Optional
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy.orm import Session

from app.db.models.patient import Patient
from app.db.models.drift_log import DriftLog

logger = logging.getLogger(__name__)

# ── Thresholds ─────────────────────────────────────────────────────────────
PSI_THRESHOLD = 0.20
KS_THRESHOLD = 0.10

# Features to monitor (must be numeric columns on the Patient model)
MONITORED_FEATURES = ["age", "bmi"]

# Number of bins used for PSI calculation
N_BINS = 10


# ── Core statistics ────────────────────────────────────────────────────────

def compute_psi(baseline: np.ndarray, current: np.ndarray, n_bins: int = N_BINS) -> float:
    """
    Compute the Population Stability Index between two distributions.

    PSI = Σ (current% - baseline%) × ln(current% / baseline%)

    Args:
        baseline: 1-D array of reference (training-time) values.
        current:  1-D array of new (production) values.
        n_bins:   Number of equal-width bins derived from the baseline.

    Returns:
        PSI score (float). Higher = more drift.
    """
    # Build bins from baseline distribution
    breakpoints = np.linspace(baseline.min(), baseline.max(), n_bins + 1)
    breakpoints[0] -= 1e-9   # ensure min value falls inside first bin
    breakpoints[-1] += 1e-9  # ensure max value falls inside last bin

    baseline_counts = np.histogram(baseline, bins=breakpoints)[0]
    current_counts = np.histogram(current, bins=breakpoints)[0]

    # Convert to proportions, replacing zeros with a small epsilon to avoid log(0)
    eps = 1e-6
    baseline_pct = np.maximum(baseline_counts / len(baseline), eps)
    current_pct = np.maximum(current_counts / len(current), eps)

    psi = np.sum((current_pct - baseline_pct) *
                 np.log(current_pct / baseline_pct))
    return float(round(psi, 6))


def compute_ks(baseline: np.ndarray, current: np.ndarray) -> float:
    """
    Compute the two-sample Kolmogorov-Smirnov statistic.

    Args:
        baseline: 1-D array of reference values.
        current:  1-D array of new values.

    Returns:
        KS statistic (float, 0–1). Higher = more distribution shift.
    """
    ks_stat, _ = stats.ks_2samp(baseline, current)
    return float(round(ks_stat, 6))


# ── Main service function ──────────────────────────────────────────────────

def run_drift_detection(
    db: Session,
    baseline_data: Optional[pd.DataFrame] = None,
    current_data: Optional[pd.DataFrame] = None,
) -> dict:
    """
    Run drift detection across all monitored features and persist results.

    If baseline_data / current_data are not provided, the function splits
    the Patient table 70/30 (oldest records = baseline, newest = current)
    to simulate a real drift scenario automatically.

    Args:
        db:            Active SQLAlchemy session.
        baseline_data: Optional DataFrame with baseline patient records.
        current_data:  Optional DataFrame with current patient records.

    Returns:
        {
            "features_checked": int,
            "drifted":          int,
            "stable":           int,
            "results": [
                {
                    "feature":       str,
                    "psi_score":     float,
                    "ks_statistic":  float,
                    "drift_detected": bool,
                    "verdict":       str,
                },
                ...
            ]
        }

    Raises:
        ValueError: If not enough patient records exist to split.
    """
    # ── 1. Load data from DB if not provided ──────────────────────────────
    if baseline_data is None or current_data is None:
        all_patients = db.query(Patient).order_by(Patient.id.asc()).all()

        if len(all_patients) < 10:
            raise ValueError(
                f"Need at least 10 patient records for drift detection, "
                f"found {len(all_patients)}. Upload more data first."
            )

        split = int(len(all_patients) * 0.70)
        baseline_records = all_patients[:split]
        current_records = all_patients[split:]

        baseline_data = pd.DataFrame([{
            "age": p.age, "bmi": p.bmi
        } for p in baseline_records])

        current_data = pd.DataFrame([{
            "age": p.age, "bmi": p.bmi
        } for p in current_records])

        logger.info(
            "Drift detection: baseline_n=%d current_n=%d",
            len(baseline_data), len(current_data),
        )

    # ── 2. Compute stats per feature ──────────────────────────────────────
    results = []
    drifted = 0

    for feature in MONITORED_FEATURES:
        if feature not in baseline_data.columns or feature not in current_data.columns:
            logger.warning(
                "Feature '%s' not found in data — skipping.", feature)
            continue

        baseline_arr = baseline_data[feature].dropna().to_numpy(dtype=float)
        current_arr = current_data[feature].dropna().to_numpy(dtype=float)

        if len(baseline_arr) < 2 or len(current_arr) < 2:
            logger.warning(
                "Feature '%s' has too few values — skipping.", feature)
            continue

        psi = compute_psi(baseline_arr, current_arr)
        ks = compute_ks(baseline_arr, current_arr)
        drift_detected = psi > PSI_THRESHOLD and ks > KS_THRESHOLD

        if drift_detected:
            drifted += 1
            verdict = "⚠️  DRIFT DETECTED — consider retraining"
        elif psi > PSI_THRESHOLD or ks > KS_THRESHOLD:
            verdict = "⚡ MODERATE — monitor closely"
        else:
            verdict = "✅ STABLE"

        # ── 3. Persist to drift_logs ───────────────────────────────────────
        log_entry = DriftLog(
            feature_name=feature,
            psi_score=psi,
            ks_statistic=ks,
            drift_detected=drift_detected,
        )
        db.add(log_entry)

        results.append({
            "feature": feature,
            "psi_score": psi,
            "ks_statistic": ks,
            "drift_detected": drift_detected,
            "verdict": verdict,
        })

        logger.info(
            "Feature '%s': PSI=%.4f KS=%.4f drift=%s",
            feature, psi, ks, drift_detected,
        )

    db.commit()

    return {
        "features_checked": len(results),
        "drifted": drifted,
        "stable": len(results) - drifted,
        "thresholds": {"psi": PSI_THRESHOLD, "ks": KS_THRESHOLD},
        "results": results,
    }
