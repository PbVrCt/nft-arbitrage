import numpy as np


class EnsembleModel:
    def __init__(self, estimators, final_estimator):
        self.__estimators = estimators
        self.__final_estimator = final_estimator
        pass

    def fit(self, X, Y):
        pred = list()
        for model in self.__estimators:
            pred.append(model.predict(X))
        pred = np.array(pred).transpose()
        self.__final_estimator.fit(pred, Y.to_numpy().ravel())
        return self

    def predict(self, X):
        pred = []
        for model in self.__estimators:
            pred.append(model.predict(X))
        pred = np.array(pred).transpose()
        return self.__final_estimator.predict(pred)
