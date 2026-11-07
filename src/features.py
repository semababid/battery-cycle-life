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
