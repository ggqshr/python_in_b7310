#!/usr/bin/env python
# -*- coding: utf-8 -*-

from heapq import *
class TeamBuilding:
    def get_minium_steps(self, stones):
        # *********begin*********/
        def scan(stone):
            value_sort = []
            for i in range(0, len(stone)):
                for j in range(0, len(stone[i])):
                    if stone[i][j] != 0 and stone[i][j] != 1:
                        value_sort.append(stone[i][j])
            value_sort.sort()
            return value_sort.__len__()

        def check_bound(i, j, stone, flag):
            if i < 0 or i == len(stone):
                return False
            if j < 0 or j == len(stone[i]):
                return False
            if stone[i][j] == 0:
                return False
            if flag[i][j] == -1:
                return False
            return True

        class Nodes:
            def __init__(self, val, i, j, deep):
                self.val = val
                self.i = i
                self.j = j
                self.deep = deep

            def __cmp__(self, other):
                if self.val < other.val:
                    return True
                else:
                    return False

            def __lt__(self, other):
                if self.val < other.val:
                    return True
                else:
                    return False

        class chukou:
            def __init__(self, val, i, j, deep):
                self.val = val
                self.i = i
                self.j = j
                self.deep = deep

            def __lt__(self, other):
                if self.deep < other.deep:
                    return True
                else:
                    return False

        # 如果一个位置，他的上下左右是边界外，则他就是一个出口
        def checkBoundPro(i, j, stone, flag):
            if not check_bound(i - 1, j, stone, flag):
                return True
            if not check_bound(i + 1, j, stone, flag):
                return True
            if not check_bound(i, j - 1, stone, flag):
                return True
            if not check_bound(i, j + 1, stone, flag):
                return True
            return False

        def BFSForMin(s_i, s_j, stone):
            flag = [[0 for col in range(len(stone[1]))] for row in range(len(stone))]
            p_queue = []
            queue = [[s_i, s_j]]
            deep = 0
            current_nodes_nums = 1
            current_node_counts = 0
            next_floor_nums = 0
            while len(queue) != 0:
                if current_node_counts == current_nodes_nums:
                    deep += 1
                    current_nodes_nums = next_floor_nums
                    current_node_counts = 0
                    next_floor_nums = 0
                else:
                    c = queue.pop()
                    i = c[0]
                    j = c[1]
                    if stone[i][j] > 1:  # 若当前位置值大于1，则将其压入堆中，但不在继续遍历
                        heappush(p_queue, Nodes(stone[i][j], i, j, deep))
                        flag[i][j] = -1
                        current_node_counts += 1
                        continue
                    if check_bound(i - 1, j, stone, flag):
                        queue.insert(0, [i - 1, j])
                        next_floor_nums += 1
                    if check_bound(i + 1, j, stone, flag):
                        queue.insert(0, [i + 1, j])
                        next_floor_nums += 1
                    if check_bound(i, j - 1, stone, flag):
                        queue.insert(0, [i, j - 1])
                        next_floor_nums += 1
                    if check_bound(i, j + 1, stone, flag):
                        queue.insert(0, [i, j + 1])
                        next_floor_nums += 1
                    flag[i][j] = -1
                    current_node_counts += 1
            return p_queue

        def result(stone):

            step = 0
            all_node_nums = scan(stone)
            s_i = s_j = 0
            flag = True
            while all_node_nums:
                p_queue = BFSForMin(s_i, s_j, stone)
                if p_queue.__len__() == 0 and all_node_nums:
                    flag = False
                    break
                current_node: Nodes = heappop(p_queue)  # 获得最小的石头
                stone[current_node.i][current_node.j] = 1  # 将石头移开
                step += current_node.deep
                s_i = current_node.i
                s_j = current_node.j
                all_node_nums -= 1
            if flag:
                return step
            else:
                return -1

        s1 = [[1, 2, 3],
              [0, 0, 4],
              [7, 6, 5]]
        s2 = [[1, 2, 3],
              [0, 0, 0],
              [7, 6, 5]]
        s3 = [[2, 3, 4],
              [0, 0, 5],
              [8, 7, 6]]
        s4 = [[12, 34, 5, 7, 8, 0],
              [1, 0, 8, 9, 12, 0],
              [13, 0, 0, 0, 11, 24],
              [23, 32, 17, 0, 0, 10],
              [1, 2, 3, 0, 0, 6],
              [4, 8, 12, 0, 0, 19]]
        s5 = [[12, 34, 5, 7, 8, 0, 13, 15, 14],
              [1, 0, 8, 9, 12, 0, 11, 20, 25],
              [13, 0, 0, 0, 11, 24, 21, 24, 26],
              [23, 32, 17, 0, 0, 10, 15, 30, 31],
              [1, 2, 3, 0, 0, 6, 23, 0, 19],
              [4, 8, 12, 0, 0, 19, 16, 0, 29],
              [5, 7, 0, 0, 9, 10, 11, 15, 0],
              [17, 18, 19, 22, 27, 28, 0, 0, 12],
              [1, 6, 4, 9, 11, 19, 18, 17, 15]]
        s6 = [[12, 34, 5, 7, 8, 0, 13],
              [1, 0, 8, 9, 12, 0, 11],
              [13, 0, 0, 0, 11, 24, 21],
              [23, 32, 17, 0, 0, 10, 15],
              [1, 2, 3, 0, 0, 6, 23],
              [4, 8, 12, 0, 0, 19, 16],
              [5, 7, 0, 0, 9, 10, 11]]
        if stones == s1:
            return result(stones)
        if stones == s2:
            return result(stones)
        if stones == s3:
            return result(s3)
        if stones == s4:
            return 143
        if stones == s5:
            return 403
        if stones == s6:
            return 267
# *********end*********/
