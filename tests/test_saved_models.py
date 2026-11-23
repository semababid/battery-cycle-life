# The app loads the models saved in models/. These checks need no data.

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

MODELS = Path(__file__).resolve().parent.parent / "models"
ALL = ["log_var", "q2", "q_max_minus_q2", "ir_change", "charge_time_first5", "t_avg_mean"]


def test_saved_models_load_and_expect_the_right_inputs():
    line = joblib.load(MODELS / "line.joblib")
    net = joblib.load(MODELS / "elastic_net.joblib")
    assert list(line.feature_names_in_) == ["log_var"]
    assert list(net.feature_names_in_) == ALL

    row = pd.DataFrame([[-4.0, 1.07, 0.005, 0.0, 10.2, 33.0]], columns=ALL)
    life_line = 10 ** line.predict(row[["log_var"]])[0]
    life_net = 10 ** net.predict(row)[0]
    assert 100 < life_line < 3000
    assert 100 < life_net < 3000


def test_saved_models_match_the_installed_scikit_learn():
    info = json.loads((MODELS / "info.json").read_text())
    assert info["scikit-learn"] == sklearn.__version__
    assert info["training cells"] == 41
    assert np.isclose(info["elastic net l1_ratio"], 0.1)
