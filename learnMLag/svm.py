import numpy as np
import matplotlib.pyplot as plt


def kernelTrans(X, A, kTup):
    m, n = np.shape(X)
    k = np.mat(np.zeros((m, 1)))
    if kTup[0] == 'lin':
        k = X * A.T
    elif kTup[0] == 'rbf':
        for j in range(m):
            deltaRow = X[j, :] - A
            k[j] = deltaRow * deltaRow.T
        k = np.exp(k / (-1 * kTup[1] ** 2))
    return k


class optStruct:
    def __init__(self, dataMatIn, classLables, C, toler, kTup):
        self.X = dataMatIn  # 数据的属性
        self.labelmat = classLables  # 数据的类别
        self.C = C  # 惩罚参数
        self.tol = toler  # 容忍度
        self.m = np.shape(dataMatIn)[0]  # 数据的数量
        self.alphas = np.mat(np.zeros((self.m, 1)))  # alphas
        self.b = 0  # b
        self.eCache = np.mat(np.zeros((self.m, 2)))
        self.K = np.mat(np.zeros((self.m, self.m)))
        for i in range(self.m):
            self.K[:, i] = kernelTrans(self.X, self.X[i, :], kTup)


def loadData(fileName):
    dataMat = []
    labelMat = []
    fr = open(fileName)
    for line in fr.readlines():
        lineArr = line.strip().split('\t')
        dataMat.append([float(lineArr[0]), float(lineArr[1])])
        labelMat.append(float(lineArr[2]))
    return dataMat, labelMat


def selectJrand(i, m):
    j = i
    while j == i:
        j = int(np.random.uniform(0, m))
    return j


def clipAlpha(aj, H, L):
    if aj > H:
        aj = H
    if L > aj:
        aj = L
    return aj


def claEK(oS: optStruct, k):
    """
    计算误差
    :param oS:svm结构
    :param k: 计算第k个alpha的误差
    :return: 误差
    """
    fxk = float(np.multiply(oS.alphas, oS.labelmat).T * oS.K[:, k] + oS.b)
    EK = fxk - float(oS.labelmat[k])
    return EK


def selectJ(i, os: optStruct, Ei):
    maxK = -1
    maxDeltaE = 0
    Ej = 0
    os.eCache[i] = [1, Ei]
    validEcacheList = np.nonzero(os.eCache[:, 0].A)[0]
    if len(validEcacheList) > 1:
        for k in validEcacheList:
            if k == i:
                continue
            Ek = claEK(os, k)
            deltaE = abs(Ei - Ek)
            if deltaE > maxDeltaE:
                maxK = k
                maxDeltaE = deltaE
                Ej = Ek
        return maxK, Ej
    else:
        j = selectJrand(i, os.m)
        Ej = claEK(os, j)
    return j, Ej


def updateEk(os: optStruct, k):
    Ek = claEK(os, k)
    os.eCache[k] = [1, Ek]


def innerL(i, os: optStruct):
    Ei = claEK(os, i)
    if (os.labelmat[i] * Ei < -os.tol and os.alphas[i] < os.C) or \
            (os.labelmat[i] * Ei > os.tol and os.alphas[i] > 0):
        j, Ej = selectJ(i, os, Ei)  # 选择相对于alpha_i计算Ei-Ej最大的j
        alphaIold = os.alphas[i].copy()
        alphaJold = os.alphas[j].copy()
        if os.labelmat[i] != os.labelmat[j]:  # 对应两种情况，选择alpha_j的上下界
            L = max(0, os.alphas[j] - os.alphas[i])
            H = min(os.C, os.C + os.alphas[j] - os.alphas[i])
        else:
            L = max(0, os.alphas[j] + os.alphas[i] - os.C)
            H = min(os.C, os.alphas[j] + os.alphas[i])
        if L == H:
            print("L==H")
            return 0
        eta = 2.0 * os.K[i, j] - os.K[i, i] - os.K[j, j]  # 计算eta
        if eta >= 0:
            print("eta>0")
            return 0
        os.alphas[j] -= os.labelmat[j] * (Ei - Ej) / eta  # 更新alpha_j
        os.alphas[j] = clipAlpha(os.alphas[j], H, L)  # 剪辑
        updateEk(os, j)  # 更新Ej
        if abs(os.alphas[j] - alphaJold) < 0.00001:
            print("j is not moving enough")
            return 0
        os.alphas[i] += os.labelmat[j] * os.labelmat[i] * (alphaJold - os.alphas[j])  # 更新alpha_i
        updateEk(os, i)  # 更新Ei
        b1 = os.b - Ei - os.labelmat[i] * (os.alphas[i] - alphaIold) * os.K[i, i] - os.labelmat[j] * \
             (os.alphas[j] - alphaJold) * os.K[i, j]
        b2 = os.b - Ej - os.labelmat[i] * (os.alphas[i] - alphaIold) * os.K[i, j] - os.labelmat[j] * \
             (os.alphas[j] - alphaJold) * os.K[j, j]
        if 0 < os.alphas[i] < os.C:
            os.b = b1
        elif 0 < os.alphas[j] < os.C:
            os.b = b2
        else:
            os.b = (b1 + b2) / 2.0
        return 1
    else:
        return 0


from numpy import mat


def smop(dataMatin, classlabels, C, toler, maxiter, ktup=('lin', 0)):
    svm = optStruct(mat(dataMatin), mat(classlabels).T, C, toler,ktup)
    iter = 0
    entireSet = True
    alphaPairsChanged = 0
    while iter < maxiter and (alphaPairsChanged > 0 or entireSet):
        alphaPairsChanged = 0
        if entireSet:
            for i in range(svm.m):
                alphaPairsChanged += innerL(i, svm)
                print("fullset ,iter:{} i :{} ,pairs changed {}".format(iter, i, alphaPairsChanged))
            iter += 1
        else:
            nonBoundIs = np.nonzero((svm.alphas.A > 0) * (svm.alphas.A < C))[0]
            for i in nonBoundIs:
                alphaPairsChanged += innerL(i, svm)
                print("non-bound,iter:{}, i:{},pair changed : {}".format(iter, i, alphaPairsChanged))
            iter += 1
        if entireSet:
            entireSet = False
        elif alphaPairsChanged == 0:
            entireSet = True
        print("iteration number : {}".format(iter))
    return svm.b, svm.alphas


def testRbf(k1=1.3):
    d, l = loadData("test")
    b, alpha = smop(d, l, 200, 0.00001, 10000, ('rbf',1.3))
    d = mat(d)
    l = mat(l).T
    svInd = np.nonzero(alpha.A > 0)[0]
    svs = d[svInd]
    labelSV = l[svInd]
    print("there is {} support vectors".format(svs.shape[0]))
    m, n = np.shape(d)
    errorCount = 0
    for i in range(m):
        kernelEval = kernelTrans(svs, d[i, :], ('rbf', k1))
        predict = kernelEval.T * np.multiply(labelSV, alpha[svInd]) + b
        if np.sign(predict)!=np.sign(l[i]):
            errorCount+=1
    print("the training error rate is {}".format(float(errorCount)/m))


def calcWs(alphas, dataArr, classLabels):  # 计算w
    X = mat(dataArr)
    labelMat = mat(classLabels).T
    m, n = np.shape(X)
    w = np.zeros((n, 1))
    for i in range(m):
        w += np.multiply(alphas[i] * labelMat[i], X[i, :].T)
    return w


if __name__ == '__main__':
    testRbf()
    # d, l = loadData("testSet.txt")
    # plt.scatter(np.array(d)[:, 0], np.array(d)[:, 1])
    # b, a = smop(d, l, 0.9, 0.001, 100)
    # ws = calcWs(a, d, l)
    # print(mat(d)[2] * mat(ws) + b)
    # print(l[2])
    # xx = np.array(np.arange(10)).reshape((10, 1))
    # y = [(-b.A[0][0] - ws[0] * xxx) / ws[1] for xxx in xx]
    # plt.plot(xx, y)
    # plt.show()
