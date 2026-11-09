# Features may only use the first `last` cycles of a cell.
# These tests change or remove everything after that and check that
# the features stay exactly the same. They use made-up data, so they
# run without the 8 GB raw files.

import numpy as np
import pandas as pd
import pytest

import src.features as features


def fake_cycles(n_cells=3, n_cycles=300, seed=0):
    rng = np.random.default_rng(seed)
    parts = []
    for c in range(n_cells):
        cycle = np.arange(1, n_cycles + 1)
        parts.append(pd.DataFrame({
            "cell_id": f"cell{c}",
            "cycle": cycle,
            "q_discharge": 1.07 - 0.0002 * cycle + rng.normal(0, 0.001, n_cycles),
            "ir": 0.017 + rng.normal(0, 0.0002, n_cycles),
            "charge_time": 10 + rng.normal(0, 0.1, n_cycles),
            "t_avg": 33 + rng.normal(0, 0.5, n_cycles),
        }))
    return pd.concat(parts, ignore_index=True)


@pytest.mark.parametrize("last", [20, 40, 60, 80, 100])
def test_summary_features_ignore_later_cycles(last):
    cycles = fake_cycles()
    before = features.summary_features(cycles, last=last)

    changed = cycles.copy()
    later = changed["cycle"] > last
    for col in ["q_discharge", "ir", "charge_time", "t_avg"]:
        changed.loc[later, col] = changed.loc[later, col] * 10 + 5
    after_changed = features.summary_features(changed, last=last)

    after_removed = features.summary_features(cycles[~later], last=last)

    pd.testing.assert_frame_equal(before, after_changed)
    pd.testing.assert_frame_equal(before, after_removed)


@pytest.mark.parametrize("first, last", [(10, 100), (10, 40)])
def test_delta_q_reads_only_the_two_cycles(monkeypatch, first, last):
    asked = []

    def fake_get_qdlin(f, i, cycle):
        asked.append(cycle)
        return np.full(1000, float(cycle))

    monkeypatch.setattr(features, "get_qdlin", fake_get_qdlin)
    dq = features.delta_q(None, 0, first, last)

    assert sorted(asked) == [first, last]
    assert np.allclose(dq, last - first)
