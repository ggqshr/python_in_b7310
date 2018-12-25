# -*- coding: utf-8 -*-
class Task:

    def sort(self, xlist):
        # ********* Begin *********#
        """
        :type xlist:list
        :param xlist:
        :return:
        """

        def print_arr(arr):
            """
            :type arr:list
            :param arr:
            :return:
            """
            for i in arr:
                if arr.index(i)!=arr.__len__()-1:
                    print(str(i) + " ", end="")
                else:
                    print(str(i))

        length = len(xlist)
        begin = 0
        end = length - 1
        flag = 0
        while begin < end:
            for i in range(begin, end):
                if xlist[i] > xlist[i + 1]:
                    tmp = xlist[i]
                    xlist[i] = xlist[i + 1]
                    xlist[i + 1] = tmp
                    print_arr(xlist)
                    flag = 1
            end -= 1
            if flag == 0:
                break
            if begin == end:
                break
            for i in range(begin + 1, end + 1)[::-1]:
                if xlist[i] < xlist[i - 1]:
                    temp = xlist[i]
                    xlist[i] = xlist[i - 1]
                    xlist[i - 1] = temp
                    print_arr(xlist)
            begin += 1
        if flag == 0:
            print_arr(xlist)


# ********* End *********#
if __name__ == '__main__':
    x1 = [4, 1, 3, 5, 2]
    x2 = [2, 3, 4, 5, 1]
    x3 = [1, 5, 4, 3, 2, 6]
    x4 = [1,2,3,4]
    t = Task()
    t.sort(x2)
