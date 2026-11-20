from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

from src.models import elastic_net

ROOT = Path(__file__).parent
DATA = ROOT / "data"

ALL = ["log_var", "q2", "q_max_minus_q2", "ir_change", "charge_time_first5", "t_avg_mean"]
SETS = {
    "Primary test": "test_primary",
    "Later batch": "test_secondary",
    "Training cells": "train",
}

st.set_page_config(page_title="Battery cycle life", layout="wide")


@st.cache_data
def load_data():
    cells = pd.read_csv(DATA / "cells_clean.csv", index_col="cell_id")
    features = pd.read_csv(DATA / "features_stage3.csv", index_col="cell_id")
    cycles = pd.read_parquet(DATA / "cycles_clean.parquet")
    curves = pd.read_parquet(DATA / "delta_q_100_10.parquet")
    voltage = np.load(DATA / "voltage_grid.npy")
    return cells, features, cycles, curves, voltage


@st.cache_resource
def fit_models(features):
    # the same two models as in notebooks 09 and 11, fitted on the 41 training cells
    train = features[features["split"] == "train"]
    y = np.log10(train["cycle_life"])
    line = LinearRegression().fit(train[["log_var"]], y)
    net = elastic_net().fit(train[ALL], y)
    return line, net


def cell_order(cell_id):
    batch, number = cell_id[1:].split("c")
    return int(batch), int(number)


cells, features, cycles, curves, voltage = load_data()
line, net = fit_models(features)
train_ids = features.index[features["split"] == "train"]

st.title("How long will this battery cell last?")
st.write(
    "The models see only the first 100 charge cycles of a cell and predict how many cycles it will last "
    "before its capacity drops to 80%. Pick a cell to see its data, what two models predict, and how long it really lasted. "
    "The data is the 124 cells from Severson et al. (2019)."
)

with st.sidebar:
    set_name = st.radio("Cells", list(SETS))
    ids = sorted(features.index[features["split"] == SETS[set_name]], key=cell_order)
    cell = st.selectbox("Cell", ids)
    st.caption(f"Charging policy: {cells.loc[cell, 'policy']}")
    st.caption(f"Batch {cells.loc[cell, 'batch']}")

row = features.loc[[cell]]
actual = row["cycle_life"].item()
pred_line = 10 ** line.predict(row[["log_var"]])[0]
pred_net = 10 ** net.predict(row[ALL])[0]

col1, col2, col3 = st.columns(3)
col1.metric("Actual life", f"{actual:,.0f} cycles")
col2.metric("Line on ΔQ variance", f"{pred_line:,.0f} cycles", f"{pred_line - actual:+,.0f} off", delta_color="off")
col3.metric("Elastic Net, 6 features", f"{pred_net:,.0f} cycles", f"{pred_net - actual:+,.0f} off", delta_color="off")

if set_name == "Training cells":
    st.caption("Both models were fitted on these cells, so predictions here are not a fair test.")
elif set_name == "Later batch":
    st.caption(
        "This batch was cycled about a year later with a changed setup. "
        "Here the one-feature line did better overall than the Elastic Net (notebook 11)."
    )

left, right = st.columns(2)

with left:
    d = cycles[(cycles["cell_id"] == cell) & (cycles["cycle"] > 1)]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axvspan(0, 100, color="tab:green", alpha=0.12, label="what the models see")
    ax.plot(d["cycle"], d["q_discharge"], color="tab:blue")
    ax.axhline(0.88, color="grey", linestyle="--", linewidth=1, label="end of life (0.88 Ah)")
    ax.axvline(actual, color="black", linewidth=1, label="actual life")
    ax.axvline(pred_line, color="tab:orange", linewidth=2, linestyle="--", label="predicted: line")
    ax.axvline(pred_net, color="tab:purple", linewidth=2, linestyle="-.", label="predicted: Elastic Net")
    ax.set_ylim(0.86, 1.1)
    ax.set_xlim(0, max(actual, pred_line, pred_net) * 1.05)
    ax.set_xlabel("cycle")
    ax.set_ylabel("discharge capacity (Ah)")
    ax.set_title("Capacity over the whole life")
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with right:
    fig, ax = plt.subplots(figsize=(6, 4))
    for other in train_ids:
        ax.plot(curves.loc[other].values, voltage, color="lightgrey", linewidth=0.7)
    ax.plot(curves.loc[cell].values, voltage, color="tab:blue", linewidth=2)
    ax.axvline(0, color="grey", linewidth=0.5)
    ax.set_xlabel("ΔQ = Q100 - Q10 (Ah)")
    ax.set_ylabel("voltage (V)")
    ax.set_title("ΔQ(V) of this cell (grey: training cells)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("A deeper, wider dip usually means a shorter life.")

with st.expander("The six features of this cell"):
    table = pd.DataFrame({
        "this cell": row[ALL].iloc[0],
        "training median": features.loc[train_ids, ALL].median(),
    })
    st.dataframe(table.style.format("{:.4f}"))
