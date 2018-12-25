import time

MIN_SUP = 2
D = (
    ("I1", "I2", 'I5'),
    ('I2', 'I4'),
    ('I2', 'I3'),
    ('I1', 'I2', 'I4'),
    ('I1', 'I3'),
    ('I2', 'I3'),
    ('I1', 'I3'),
    ('I1', 'I2', 'I3', 'I5'),
    ('I1', 'I2', 'I3')
)


def random_get_set(data: list, current_count: int, ll: list, index: int, aim_count: int, result: list):
    """
    :param data: 记录当前已经抽取的数据
    :param current_count: 当前的深度
    :param ll: 要抽取的列表
    :param index: 从第几个元素开始抽取
    :param aim_count: 目标深度
    :param result: 结果的列表
    """
    if current_count == aim_count:  # 如果到达指定的深度
        result.append(data.copy())
    else:
        for i in range(index + 1, ll.__len__()):
            data.append(ll[i])
            random_get_set(data, current_count + 1, ll, i, aim_count, result)
            data.remove(ll[i])


def get_subset_by_nums(s, num: int) -> list:
    """
    从给定列表中抽取指定数目的组合
    :param s:
    :param num:
    :return:
    """
    result = []
    size = len(s)
    for i in range(size + 1 - num):
        data = [s[i]]
        random_get_set(data, 1, s, i, num, result)
    return result


def count_tuple_at_list(mode, string) -> int or None:
    """
    在串中统计指定的模式的数量
    :param mode: 要统计的模式
    :param string: 目标串
    :return:数量
    """
    count_all = 0
    for s in string:
        flag = 1
        for m in mode:
            if s.count(m) == 0:
                flag = 0
        if flag == 1:
            count_all += 1
    return count_all


def get_frequent_1_itemsets() -> list:
    """
    得到频繁1项集
    :return:
    """
    flaten_D = flaten_data()
    L_one = {}
    for i in flaten_D:
        if i not in L_one.keys():
            L_one[i] = int(flaten_D.count(i))
    L_one[22] = 1
    return [[x[0]] for x in filter(lambda x: x[1] >= MIN_SUP, L_one.items())]


def flaten_data():
    """
    压平数据
    :return:
    """
    result = []
    for d in D:
        result.extend(list(d))
    return result


def judge_union(l1: list, l2: list):
    if l1.__len__() == 1:
        if l1[0] < l2[0]:
            return True
    else:
        size = l1.__len__()
        if l1[0:size - 1] == l2[0:size - 1] and l1[-1] < l2[-1]:
            return True
    return False


def gen_apriori(l_k_1):
    """
    :type l_k_1:list
    :param l_k_1:
    :return:
    """
    result = []
    size = l_k_1.__len__()
    for i in range(size):
        for j in range(i + 1, size):
            if judge_union(l_k_1[i], l_k_1[j]):
                c = l_k_1[i].copy()
                c.append(l_k_1[j][-1])
                if not judge_and_cut(c, l_k_1):
                    result.append(c)
    return result


def judge_and_cut(c, l_k_1):
    """
    判断是否进行剪枝
    :param c:
    :param l_k_1:
    :return:
    """
    for subset in get_subset_by_nums(c, len(c) - 1):
        if subset not in l_k_1:
            return True
    return False


def apriori():
    """
    apriori本体
    :return:
    """
    l_k_1 = get_frequent_1_itemsets()
    l_i = sorted(l_k_1)
    while True:
        c_i = gen_apriori(l_i)  # 产生所有候选
        c_i_dict = {}
        for c in c_i:
            count = count_tuple_at_list(c, D)  # 记录C中的候选的支持计数
            c_i_dict[",".join(c)] = count
        new_l_i = [x[0].split(",") for x in filter(lambda x: x[1] >= MIN_SUP, c_i_dict.items())]
        if new_l_i.__len__() == 0:
            return l_i
        l_i = new_l_i


if __name__ == '__main__':
    print(apriori())
