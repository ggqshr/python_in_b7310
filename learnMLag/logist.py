from numpy import *
import matplotlib.pyplot as plt
import pandas as pda


def sigmod(X):
    return 1 / (1 + exp(-X))


def h(theta, X):
    return sigmod(X @ theta)


def computLoss(theta, X, Y):
    data_num = X.shape[0]
    hx = h(theta, X)
    loss = -sum((Y * log(hx) + (1 - Y) * log(1 - hx)))
    loss = loss / data_num
    grad = (X.T @ (hx - Y)) / data_num
    return loss, grad


def train(X, Y, LR=1e-2, num_iters=8000):
    num_data, num_label = X.shape
    theta = 0.001 * random.randn(num_label, 1).reshape((-1, 1))
    loss = []
    error, dw = computLoss(theta, X, Y)
    for i in range(num_iters):
        theta -= LR * dw
        loss.append(error)
        error, dw = computLoss(theta, X, Y)

    return theta, loss


def load_data(file_name):
    data = pda.read_csv(file_name)
    return data


def trans_data():
    from svm import loadData
    data, label = loadData("testSet.txt")
    column = ["x1", 'x2', 'y']
    dd = pda.DataFrame(hstack((array(data).reshape((-1, 2)), array(label).reshape((-1, 1)))), columns=column)
    dd.loc[dd.y == -1, 'y'] = 0
    dd.to_csv("testSet.csv")


if __name__ == '__main__':
    all_data = load_data("testSet.csv")
    all_data = all_data.values
    data = all_data[:, 1:3].reshape((-1, 2))
    label = all_data[:, 3].reshape((-1, 1))
    data = hstack((ones((data.shape[0], 1)),data))
    plt.scatter(data[:, 1], data[:, 2])
    theta,loss = train(data,label)
    xx = arange(0,10,0.5)
    yy = (- theta[0] - theta[1]*xx) / theta[2]
    plt.plot(xx,yy)
    # plt.plot(loss)
    plt.show()

