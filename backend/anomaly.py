import numpy as np

# -----------------------------------------------------
# BASELINE DISTRIBUTION (NORMAL BEHAVIOR)
# -----------------------------------------------------

np.random.seed(42)

# Normal behavior: time_delta ~ Uniform(0.5, 2.0)
normal_time_deltas = np.random.uniform(0.5, 2.0, 500)

BASELINE_MEAN = np.mean(normal_time_deltas)
BASELINE_STD = np.std(normal_time_deltas)

# -----------------------------------------------------
# ANOMALY SCORING FUNCTION
# -----------------------------------------------------

def compute_anomaly_score(state_index, time_delta):
    """
    Deterministic anomaly scoring using Z-score scaling.
    Produces strong magnitude-based separation.
    """

    # Compute Z-score
    z_score = (time_delta - BASELINE_MEAN) / BASELINE_STD

    # Convert to positive anomaly magnitude
    anomaly_strength = abs(z_score)

    # Scale to 0–1 range (aggressive scaling)
    normalized = anomaly_strength / 10

    # Clamp
    normalized = max(0.0, min(1.0, normalized))

    return float(z_score), normalized