import math


# -*- coding: utf-8 -*-
class Task:

    def solve(self, x1, y1, r1, x2, y2, r2):
        import math
        d = math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
        r = float(r1 + r2)
        if d >= r:  # 圆心之间距离大于两个半径之和，相切或者相离,总面积相加即可
            return math.pi * r1 * r1 + math.pi * r2 * r2
        elif d <= abs(r2 - r1):  # 小圆包在大圆里
            if r1 > r2:
                return math.pi * r1 * r1
            else:
                return math.pi * r2 * r2
        else:  # 两圆相交的情况，为两圆的面积相加，然后减去中间相交的部分你的面积
            ang1 = math.acos((r1 * r1 + d * d - r2 * r2) / (2 * r1 * d))
            ang2 = math.acos((r2 * r2 + d * d - r1 * r1) / (2 * r2 * d))
            jd = ang1 * r1 * r1 + ang2 * r2 * r2 - r1 * d * math.sin(ang1)
            return (math.pi * r1 * r1 + math.pi * r2 * r2) - jd


if __name__ == '__main__':
    ss = Task()
    s = ss.solve(0, 0, 1, 1, 1, 1)
    print(s)
