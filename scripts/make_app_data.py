# Builds the small data bundle the app needs, in app_data/, from the tables
# the notebooks write to data/. The bundle is committed, so the app can run
# without the 8 GB download (for example on Streamlit Community Cloud).
#
# Run from the repo folder after notebooks 01 to 07:  python scripts/make_app_data.py

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "app_data"
OUT.mkdir(exist_ok=True)

# one row per cell: batch, policy, split, life and the six model inputs (full precision)
cells = pd.read_csv(DATA / "cells_clean.csv", index_col="cell_id")
features = pd.read_csv(DATA / "features_stage3.csv", index_col="cell_id")
table = cells[["batch", "policy"]].join(features)
table.to_csv(OUT / "cells.csv")

# capacity per cycle, only what the plot needs; float32 is plenty for a plot
cycles = pd.read_parquet(DATA / "cycles_clean.parquet", columns=["cell_id", "cycle", "q_discharge"])
cycles = cycles[cycles["cycle"] > 1]
cycles["cycle"] = cycles["cycle"].astype("int16")
cycles["q_discharge"] = cycles["q_discharge"].astype("float32")
cycles.to_parquet(OUT / "capacity.parquet", index=False)

# delta Q curves (cycle 100 minus 10) and the voltage grid, for the second plot
curves = pd.read_parquet(DATA / "delta_q_100_10.parquet").astype("float32")
curves.to_parquet(OUT / "delta_q.parquet")
np.save(OUT / "voltage.npy", np.load(DATA / "voltage_grid.npy"))

size = sum(f.stat().st_size for f in OUT.iterdir()) / 1e6
print(f"wrote {len(table)} cells to {OUT} ({size:.1f} MB)")
