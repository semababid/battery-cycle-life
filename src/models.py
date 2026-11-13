import numpy as np
from sklearn.linear_model import ElasticNetCV
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def elastic_net():
    # scale the features, then an Elastic Net that picks its own shrinkage
    # with a 5-fold cross-validation on whatever data it is fitted on
    inner = KFold(n_splits=5, shuffle=True, random_state=1)
    return make_pipeline(StandardScaler(), ElasticNetCV(l1_ratio=[0.1, 0.5, 0.9, 1.0], cv=inner, max_iter=50000))


def rmse(y, p):
    # root mean squared error, in the units of y (cycles)
    return np.sqrt(np.mean((y - p) ** 2))


def mape(y, p):
    # mean absolute percentage error
    return np.mean(np.abs(y - p) / y) * 100
