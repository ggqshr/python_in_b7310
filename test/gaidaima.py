#!/usr/bin/env python
# -*- coding: utf-8 -*-
class BestTeam:
    def get_best_team(self, numbers, abilities, selectedNum, distance):
        N = numbers
        abilities = abilities
        k = selectedNum
        d = distance
        print(N)
        print(abilities)
        print(k)
        print(d)
        dp = [(each, each) for each in abilities]
        for i in range(1, k):
            dp_ = dp[:i]
            for j in range(i, N):
                temp_list = []
                for z in range(j - d, j):
                    if z < 0:
                        continue
                    else:
                        temp_list.append(abilities[j] * dp[z][0])
                        temp_list.append(abilities[j] * dp[z][1])
                dp_.append((max(temp_list), min(temp_list)))
            dp = dp_
        print(max([max(each) for each in dp]))
