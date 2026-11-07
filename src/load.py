import h5py

DATA = "data/raw/"
BATCH_FILES = {
    1: "2017-05-12_batchdata.mat",
    2: "2017-06-30_batchdata.mat",
    3: "2018-04-12_batchdata.mat",
}


def open_batch(batch, root=""):
    return h5py.File(root + DATA + BATCH_FILES[batch], "r")


def n_cells(f):
    return f["batch"]["cycle_life"].shape[0]


def get_value(f, field, i):
    # number stored behind a reference, e.g. cycle_life of cell i
    ref = f["batch"][field][i, 0]
    return f[ref][()].item()


def get_text(f, field, i):
    # text is stored as character codes
    ref = f["batch"][field][i, 0]
    return "".join(chr(c) for c in f[ref][()].flatten())


def get_summary(f, i):
    # per-cycle summary values of cell i, as a dict of 1D arrays
    group = f[f["batch"]["summary"][i, 0]]
    return {key: group[key][0, :] for key in group.keys()}


def get_qdlin(f, i, cycle):
    # discharge capacity of one cycle on the fixed Vdlin voltage grid.
    # `cycle` is the cycle number as in the summary (starts at 1).
    # The curves are stored from position 0, so cycle n is at position n - 1.
    cyc = f[f["batch"]["cycles"][i, 0]]
    return f[cyc["Qdlin"][cycle - 1, 0]][()].flatten()


def get_vdlin(f):
    return f[f["batch"]["Vdlin"][0, 0]][()].flatten()
