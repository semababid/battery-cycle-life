# The app runs from the small bundle in app_data/ and the saved models in models/.
# Both are committed, so these checks run without the raw data. They make sure
# the bundle and the models together still give the reported test scores.

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ALL = ["log_var", "q2", "q_max_minus_q2", "ir_change", "charge_time_first5", "t_avg_mean"]


def rmse(y, p):
    return np.sqrt(np.mean((y - p) ** 2))


def test_bundle_has_all_cells():
    cells = pd.read_csv(ROOT / "app_data" / "cells.csv", index_col="cell_id")
    assert len(cells) == 124
    assert cells["split"].value_counts().to_dict() == {"test_primary": 43, "test_secondary": 40, "train": 41}
    curves = pd.read_parquet(ROOT / "app_data" / "delta_q.parquet")
    assert set(curves.index) == set(cells.index)
    capacity = pd.read_parquet(ROOT / "app_data" / "capacity.parquet")
    assert set(capacity["cell_id"]) == set(cells.index)


def test_bundle_and_models_give_the_reported_scores():
    cells = pd.read_csv(ROOT / "app_data" / "cells.csv", index_col="cell_id")
    line = joblib.load(ROOT / "models" / "line.joblib")
    net = joblib.load(ROOT / "models" / "elastic_net.joblib")
    reported = {"test_primary": (137.9, 113.7), "test_secondary": (195.9, 262.4)}
    for split, (want_line, want_net) in reported.items():
        d = cells[cells["split"] == split]
        y = d["cycle_life"].values
        assert round(rmse(y, 10 ** line.predict(d[["log_var"]])), 1) == want_line
        assert round(rmse(y, 10 ** net.predict(d[ALL])), 1) == want_net
