'''
利用一个数组复制题目给的数组，然后进行遍历，如果遇到+，则与其相连的所有+都变成o
然后count++，
'''


def countOfShips(ferry):
    f1 = ferry

    def trave(i, j, ff):
        if i < 0 or i == len(ff) or j < 0 or j == len(ff[0]):  # 如果越界了直接返回
            return
        ff[i][j] = 'x'
        # 如果没越界 就把他的上下左右都变成o
        if i - 1 >= 0 and ff[i - 1][j] == 'o':
            trave(i - 1, j, ff)
        if i + 1 < len(ff) and ff[i + 1][j] == 'o':
            trave(i + 1, j, ff)
        if j - 1 >= 0 and ff[i][j - 1] == 'o':
            trave(i, j - 1, ff)
        if j + 1 < len(ff[i]) and ff[i][j + 1] == 'o':
            trave(i, j + 1, ff)

    result = 0
    for ii in range(len(ferry)):
        for jj in range(len(ferry[0])):
            if f1[ii][jj] == 'o':
                trave(ii, jj, f1)
                result += 1
    return result


if __name__ == '__main__':
    ssss = "x o x o x x".split()
    s1 = "x x x o o x".split()
    s2 = "x o x x x x".split()
    s3 = "x o x o o x".split()
    sss = [ssss, s1, s2, s3]
    ss = countOfShips(sss)
    print(ss)
