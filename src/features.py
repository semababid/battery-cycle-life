import numpy as np
import pandas as pd

from src.load import open_batch, n_cells, get_qdlin, get_vdlin


def delta_q(f, i, first=10, last=100):
    # Q(V) at cycle `last` minus Q(V) at cycle `first`, on the fixed Vdlin grid
    return get_qdlin(f, i, last) - get_qdlin(f, i, first)


def delta_q_all(cell_ids, root="", first=10, last=100):
    # delta Q curve for every cell in cell_ids, one row per cell.
    # Returns (DataFrame with cell_id as index and 1000 columns, voltage grid)
    curves = {}
    voltage = None
    for batch in [1, 2, 3]:
        f = open_batch(batch, root=root)
        if voltage is None:
            voltage = get_vdlin(f)
        for i in range(n_cells(f)):
            cell = f"b{batch}c{i}"
            if cell in cell_ids:
                curves[cell] = delta_q(f, i, first, last)
        f.close()
    return pd.DataFrame.from_dict(curves, orient="index"), voltage


def log_var(curves):
    # the paper's single feature: log10 of the variance of each delta Q curve
    return np.log10(curves.var(axis=1, ddof=0))


def summary_features(cycles, last=100):
    # simple features from the per-cycle summary, one row per cell.
    # Uses cycles 2 to `last` only (cycle 1 is empty in batch 1).
    # nan-aware because of the glitches at cycles 12 and 13 in batch 1.
    # Some features read single cycles (2 to 6 and `last`). If one of those is
    # missing, stop with a clear error instead of returning a silent NaN.
    window = cycles[(cycles["cycle"] >= 2) & (cycles["cycle"] <= last)]
    rows = {}
    for cell, d in window.groupby("cell_id"):
        d = d.set_index("cycle")
        for n in [2, 3, 4, 5, 6, last]:
            if n not in d.index:
                raise ValueError(f"{cell}: cycle {n} is missing")
        if pd.isna(d.loc[2, "q_discharge"]) or d.loc[[2, last], "ir"].isna().any():
            raise ValueError(f"{cell}: capacity at cycle 2 or resistance at cycle 2 or {last} is missing")
        rows[cell] = {
            "q2": d.loc[2, "q_discharge"],
            "q_max_minus_q2": d["q_discharge"].max() - d.loc[2, "q_discharge"],
            "ir_change": d.loc[last, "ir"] - d.loc[2, "ir"],
            "charge_time_first5": d.loc[2:6, "charge_time"].mean(),
            "t_avg_mean": d["t_avg"].mean(),
        }
    return pd.DataFrame.from_dict(rows, orient="index")
