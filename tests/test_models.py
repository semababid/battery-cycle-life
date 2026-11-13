import numpy as np

from src.models import elastic_net, mape, rmse


def test_rmse_and_mape_on_known_numbers():
    y = np.array([100.0, 200.0])
    p = np.array([110.0, 180.0])
    assert np.isclose(rmse(y, p), np.sqrt((10**2 + 20**2) / 2))
    assert np.isclose(mape(y, p), 10.0)
    assert rmse(y, y) == 0


def test_elastic_net_gives_the_same_fit_every_time():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 3))
    y = 2 * X[:, 0] + rng.normal(0, 0.1, 40)
    first = elastic_net().fit(X, y)
    second = elastic_net().fit(X, y)
    assert np.allclose(first.predict(X), second.predict(X))
    assert abs(first[-1].coef_[0]) > abs(first[-1].coef_[1])
