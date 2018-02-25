#! /usr/bin/python
# -*- coding: UTF-8 -*-
import csv
import math
from collections import defaultdict, OrderedDict
from itertools import combinations


def getdata(file_path, minimum_score):
    """
    读取csv文件的数据，并根据给定的分数值筛选符合要求的数据，并以字典的形式返回
    :param file_path: 数据文件的存放路径
    :param minimum_score: 符合要求的最低分数值
    :return: 返回table，table的key是学生的学号，每个key对应的value是该学生符合要求的课程
    """
    with open(file_path) as f:
        f_csv = csv.reader(f)
        table = defaultdict(list)
        for line in f_csv:
            if int(line[2]) >= minimum_score \
                    and line[1] not in table[line[0]]:
                table[line[0]].append(line[1])
        for key in table:
            table[key].sort()
    return table


def genl1(table, min_support):
    """
    产生频繁一项集
    :param table: 数据表 
    :param min_support: 最小支持度
    :return: 返回频繁一项集
    """
    c1 = {}
    keys = []
    for stu in table:
        for course in table[stu]:
            if course in c1:
                c1[course] += 1
            else:
                keys.append(course)
                c1[course] = 1
    keys.sort()
    l1 = OrderedDict(((key,), c1[key]) for key in keys if c1[key] >= min_support)
    return l1


def has_infrequent_subset(c, l_pre):
    """
    根据Apriori算法的先验性质，进行剪枝处理
    :param c: 新生成的候选项K集中的某一项 
    :param l_pre: 频繁(k-1)项集
    :return: 
    """
    for item in c:
        tmpsubset = list(c - {item})
        tmpsubset.sort()
        if not {tuple(tmpsubset)}.issubset(set(l_pre.keys())):
            return True
    return False


def apriori_gen(l_pre):
    """
    生成候选K项集
    :param l_pre: 频繁K-1项集  
    :return: 候选K项集c_next
    """
    keys = list()
    l_pre_key_list = list(l_pre.keys())
    l_pre_key_list.sort()
    for idx, item1 in enumerate(l_pre_key_list):
        for i in range(idx + 1, len(l_pre_key_list)):
            item2 = l_pre_key_list[i]
            if item1[:-1] == item2[:-1] and\
                    not has_infrequent_subset(set(item1) | set(item2), l_pre):
                item = list(set(item1) | set(item2))
                item.sort()
                keys.append(item)
    c_next = OrderedDict((tuple(key), 0) for key in keys)
    return c_next


def calc_support(c, table, min_support):
    """
    计算候选项集c的支持数，得出频繁项集
    :param c: 候选项集
    :param table: 数据表
    :param min_support: 最小支持数 
    :return: 满足最小支持数的频繁项集
    """
    for key in c.keys():
        for stu in table:
            if set(key).issubset(table[stu]):
                c[key] += 1
    l = OrderedDict((k, v) for k, v in c.items() if v >= min_support)
    return l


def apriori(l1, table, min_support):
    """
    apriori挖掘频繁项集算法
    :param l1: 频繁一项集
    :param table: 数据表
    :param min_support: 最小支持度 
    :return: 所有的频繁项集
    """
    all_ls = list()
    l_next = l1
    while len(l_next) != 0:
        all_ls.append(l_next)
        print('l_%d length:' % len(all_ls), len(l_next))
        c_next = apriori_gen(l_next)
        l_next = calc_support(c_next, table, min_support)
    return all_ls


def generate_rules(l, all_ls, support, min_confident):
    """
    关联规则生成算法
    :param l: 频繁项集
    :param all_ls: 所有的频繁项集，记录了每个频繁项集的支持度
    :param support: 频繁项集l的支持度
    :param min_confident: 最小置信度
    """
    course = {}
    with open('course.csv') as f:
        course_csv = csv.reader(f)
        for line in course_csv:
            course[line[0]] = line[1]
    subsets = []
    length = len(l)
    for i in range(1, length):
        subsets.append(list(combinations(l, i)))
    for subset in subsets:
        for item in subset:
            tmp = list(set(l) - set(item))
            tmp.sort()
            cnfd = support / all_ls[len(item) - 1][item]
            if cnfd >= min_confident:
                a = [course[i] for i in item]
                b = [course[i] for i in tmp]
                print(a, '-->', b, ' 置信度:', cnfd, sep='')


if __name__ == '__main__':
    file = '2011.csv'
    score = 90
    score_table = getdata(file, score)
    min_support = math.ceil(len(score_table) * 0.25)   # 计算最小支持数，向上取整
    min_confident = 0.5
    print('Number of Student:', len(score_table))
    print('Min_Support:', min_support)
    print('Min_Confident:', min_confident)
    l1 = genl1(score_table, min_support)
    all_ls = apriori(l1, score_table, min_support)
    l = all_ls[-1]
    for item in l:
        generate_rules(list(item), all_ls, l[item], min_confident)
