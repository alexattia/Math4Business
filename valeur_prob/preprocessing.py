import numpy as np
from datetime import datetime

def rescalling(X):
	"""
	Input X
	Output X in [0,1]
	"""
	m = X.min()
	M = X.max()
	Y = (X - m) / (M - m)
	return Y

def rescalling_mean(X):
	"""
	Input X
	Output X in [-1,1]
	"""
	mean = X.mean()
	m = X.min()
	M = X.max()
	Y = (X - mean) / (M - m)
	return Y

def log_transformation(X, thres, mult):
    """
    Input X
    Output log(X) - thres
    """
    Y = np.log10(X)*mult
    Y = Y - thres
    return Y

def sigmoid6(X):
    """
    Input X in [-1,1]
    Return [0,1]
    sigmoid(6) = 0.9975
    sigmoid(-6) = 0.0025
    """
    return np.exp(6 * X) / (1 + np.exp(6 * X))


def cap_floor(X, cap, floor):
	"""
	Input X
	Return X in [floor + |m|, cap + |m|]
	"""
	m = np.abs(X.min())
	Y = X
	Y[X > cap] = cap + m + 1
	Y[X < floor] = floor + m + 1
	return Y

def date_difference(x):
	return (datetime.today() - datetime.strptime(x, "%Y-%m-%d")).days
