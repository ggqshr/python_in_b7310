'''
给定目录，按照一定格式输出遍历当前文件夹,但是只输出图片格式的文件
'''
import sys, os


def showDirTree(path):
    ss = list()
    deep = 0
    suffext = ("jpg", "png", "bmp")
    if os.path.isdir(path):
        ss.append("+--" + os.path.split(path)[-1])
        deep += 1

    def trave(dir, deep, ss):
        if not os.path.isdir(dir):  # 若当前不是目录
            ss.append((2 * deep) * " " + "--" + dir)
            return
        dirs = os.listdir(dir)  # 获得当前目录下的所有文件
        for d in dirs:
            if os.path.isdir(os.path.join(dir, d)):  # 如果是文件夹
                ss.append((2 * deep) * " " + "+--" + d)
                trave(os.path.join(dir, d), deep + 1, ss)
            else:  # 如果是文件
                if d.endswith(suffext):
                    ss.append((2 * deep) * " " + "--" + d)

    trave(path, deep, ss)
    for i in ss:
        print(i)


if __name__ == '__main__':
    ss = showDirTree("C:\\Users\\ggq\\Downloads\\Compressed\\root")
