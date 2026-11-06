#!/usr/bin/env bash
# Downloads the three MATR batches used in Severson et al. (2019), about 8.3 GB in total.
# -C - resumes a broken download.
set -euo pipefail
cd "$(dirname "$0")/../data/raw"
base=https://data.matr.io/1/api/v1/file
curl -L -C - -o 2017-05-12_batchdata.mat "$base/5c86c0b5fa2ede00015ddf66/download"
curl -L -C - -o 2017-06-30_batchdata.mat "$base/5c86bf13fa2ede00015ddd82/download"
curl -L -C - -o 2018-04-12_batchdata.mat "$base/5c86bd64fa2ede00015ddbb2/download"
