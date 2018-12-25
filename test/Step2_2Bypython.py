# -*- coding: utf-8 -*-
class Operation:
    def __init__(self, op, x, y):
        self.op = op
        self.x = x
        self.y = y


class Task:

    def calLeft(self, data, L, R):
        result = 0
        for i in range(L, R + 1):
            result += data[i] * (i - L + 1)
        return result

    def calRight(self, data, L, R):
        result = 0
        for i in range(L, R + 1):
            result += data[i] * (R - i + 1)
        return result

    def pjStr(self, op):
        """
        :type op:Operation
        :param op:
        :return:
        """
        return op.op + str(op.x) + str(op.y)

    def solve(self, data, operations):
        count = 0
        resultMap = {}
        for op in operations:  # type:Operation
            if op.op == "L":  # 求左边的和
                L = op.x
                R = op.y
                rr = self.calLeft(data, L, R)
                pjOp = self.pjStr(op)
                if pjOp in resultMap.keys():
                    count += resultMap.get(pjOp)
                else:
                    count += rr
                    resultMap[pjOp] = rr

            elif op.op == "R":  # 求右边的和
                L = op.x
                R = op.y
                pjOp = self.pjStr(op)
                rr = self.calRight(data, L, R)
                if pjOp in resultMap.keys():
                    count += resultMap.get(pjOp)
                else:
                    count += rr
                    resultMap[pjOp] = rr

            elif op.op == "C":  # 替换
                x = op.x
                y = op.y
                data[x] = y
                resultMap.clear()

        return int(count % (1e9 - 7))






if __name__ == '__main__':
    t = Task()
    data = [16, 15, 10, 2, 18, 16, 6, 5, 12, 19]
    operations = [
        Operation('C', 3, 6),
        Operation('L', 2, 6),
        Operation('C', 7, 19),
        Operation('C', 1, 18),
        Operation('R', 7, 8),
        Operation('L', 7, 7),
        Operation('L', 4, 9),
        Operation('R', 5, 5),
        Operation('R', 2, 8),
        Operation('R', 2, 8),
    ]
    print(t.solve(data, operations))
