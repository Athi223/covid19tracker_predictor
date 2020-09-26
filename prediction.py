from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

class Prediction:
    def __init__(self, x_data, y_data):
        X = np.array(x_data).reshape(-1, 1)
        self.poly = PolynomialFeatures()                 # default degree=2
        x_poly = self.poly.fit_transform(X)
        self.poly.fit(x_poly, y_data)
        self.regression = LinearRegression()
        self.regression.fit(x_poly, y_data)

    def predictor(self, x_input):
        return int(self.regression.predict(self.poly.fit_transform(np.array(x_input).reshape(-1, 1)))[0])

class Confirmed(Prediction):
    pass

class Active(Prediction):
    pass

class Deceased(Prediction):
    pass

class Recovered(Prediction):
    pass