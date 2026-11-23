# Fits the two final models on the 41 training cells and saves them in models/,
# so the app can load them instead of fitting on every start.
# Same recipe as notebooks 09 and 11. Needs data/features_stage3.csv (notebook 07).
#
# Run from the repo folder:  python scripts/save_models.py

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
from src.models import elastic_net  # noqa: E402

ALL = ["log_var", "q2", "q_max_minus_q2", "ir_change", "charge_time_first5", "t_avg_mean"]

features = pd.read_csv(ROOT / "data" / "features_stage3.csv", index_col="cell_id")
train = features[features["split"] == "train"]
y = np.log10(train["cycle_life"])

line = LinearRegression().fit(train[["log_var"]], y)
net = elastic_net().fit(train[ALL], y)

out = ROOT / "models"
out.mkdir(exist_ok=True)
joblib.dump(line, out / "line.joblib")
joblib.dump(net, out / "elastic_net.joblib")

info = {
    "target": "log10(cycle life)",
    "training cells": len(train),
    "line inputs": ["log_var"],
    "elastic net inputs": ALL,
    "elastic net alpha": round(float(net[-1].alpha_), 6),
    "elastic net l1_ratio": float(net[-1].l1_ratio_),
    "scikit-learn": sklearn.__version__,
}
(out / "info.json").write_text(json.dumps(info, indent=2) + "\n")
print(f"saved 2 models to {out} (fitted on {len(train)} training cells)")
