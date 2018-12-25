import numpy as np
import pandas as pda
import matplotlib.pyplot as plt

LR = 1e-2

data = pda.read_csv("./ex1data1.txt")

data_matrix = data.values

X_1 = data_matrix[:, 0].reshape((96, 1))
Y = data_matrix[:, 1].reshape((96, 1))
X_0 = np.ones((96, 1))

X = np.hstack((X_0, X_1))


def loss_function(theta, X, Y):
    diff = X @ theta - Y  # type:np.ndarray
    return (1. / 2 * X.shape[0]) * (diff.T @ diff)


def gradient_func(theta, X, Y):
    diff = X @ theta - Y
    return (1. / X.shape[0]) * (X.T @ diff)


def gradient_down(X, Y):
    theta = np.ndarray([1, 2]).reshape((2, 1))
    loss = loss_function(theta, X, Y)
    gradient = gradient_func(theta, X, Y)
    loss_result = [loss[0]]
    count = 1
    while np.all(np.abs(gradient) > 1e-3):
        theta = theta - LR * gradient
        loss_result.append(loss_function(theta, X, Y))
        count += 1
        gradient = gradient_func(theta, X, Y)
    return theta, loss_result, count


theta, loss, count = gradient_down(X, Y)
# plt.plot(np.arange(0, count), loss)
plt.scatter(X_1, Y)
plt.plot(X_1, X @ theta)
plt.show()
