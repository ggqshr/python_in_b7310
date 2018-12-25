'''
给定目录，按照一定格式输出遍历当前文件夹
'''
import sys, os


def showDirTree(path):
    ss = list()
    deep = 0
    if os.path.isdir(path):
        ss.append("+--" + os.path.split(path)[-1] + "\n")
        deep += 1

    def trave(dir, deep, ss):
        if not os.path.isdir(dir):  # 若当前不是目录
            ss.append((2 * deep) * " " + "--" + dir + "\n")
            return
        dirs = os.listdir(dir)  # 获得当前目录下的所有文件
        for d in dirs:
            if os.path.isdir(os.path.join(dir, d)):  # 如果是文件夹
                ss.append((2 * deep) * " " + "+--" + d + "\n")
                trave(os.path.join(dir, d), deep + 1, ss)
            else:  # 如果是文件
                ss.append((2 * deep) * " " + "--" + d + "\n")

    trave(path, deep, ss)
    for i in ss:
        print(i)


if __name__ == '__main__':
    ss = showDirTree("C:\\Users\\ggq\\Downloads\\Compressed\\root")
    for i in ss:
        print(i)
