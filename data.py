import numpy as np
import pandas as pd
from config import FEATURES

RANGES = {
    "C3S": (40.0, 70.0),
    "C2S": (10.0, 30.0),
    "C3A": (5.0, 15.0),
    "C4AF": (5.0, 15.0),
    "Gypsum": (2.0, 6.0),
    "Fineness": (2500.0, 4000.0),
    "Water_cement": (0.30, 0.60),
    "Temperature": (15.0, 45.0),
    "Humidity": (25.0, 95.0),
    "MixTime": (60.0, 300.0),
}

def generate_dummy_data(n=800, seed=42):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        k: rng.uniform(*RANGES[k], n) for k in FEATURES
    })

    base = (
        0.48 * df["C3S"]
        - 25.0 * df["Water_cement"]
        + 0.007 * df["Fineness"]
        + 0.22 * df["Gypsum"]
        + 0.08 * df["C3A"]
        - 0.05 * df["Humidity"]
        + 0.10 * df["Temperature"]
        + 0.005 * df["MixTime"]
        - 0.04 * df["C4AF"]
        + 0.03 * df["C2S"]
    )

    nonlin = (
        - 0.12 * (df["Water_cement"] ** 2) * 100
        + 0.000002 * (df["Fineness"] - 3200.0) ** 2
        - 0.0008 * (df["Humidity"] - 60.0) ** 2
        + 0.0004 * (df["Temperature"] - 30.0) ** 2
        + 0.03 * (df["C3S"] * df["Gypsum"] / 100.0)
    )

    noise = rng.normal(0, 2.0, n)
    df["Strength"] = base + nonlin + noise
    return df

def feature_bounds():
    return RANGES.copy()
