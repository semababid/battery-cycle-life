# battery-cycle-life

Predicting how many charge cycles a lithium-ion cell will last, using only its first 100 cycles.

The data comes from Severson et al. (2019), "Data-driven prediction of battery cycle life before capacity degradation", Nature Energy. The three batch files hold 140 LFP/graphite cells (A123 APR18650M1A, 1.1 Ah), each charged with a different fast-charging policy until it lost 20% of its capacity. The paper uses 124 of them. Working out which cells were dropped, and why, is part of this project.

This is work in progress. So far the repo only explores the raw files.

## Setup

Python 3.13:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/download_data.sh
```

The download script fetches the three batches from data.matr.io (about 8.3 GB) into `data/raw/`, which git ignores.

## Layout

- `notebooks/` exploration, in the order I did it
- `src/` code the notebooks share
- `reports/figures/` saved plots
- `scripts/` data download
